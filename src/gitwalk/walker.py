import os
from pathlib import Path
from typing import Iterator, List, Literal, Tuple
from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern

def gitwalk(top: str, topdown: Literal[True] = True, onerror=None, followlinks: bool = False) -> Iterator[Tuple[str, List[str], List[str]]]:
    """
    Walk a directory tree similar to os.walk(), but respecting .gitignore rules.
    
    Args:
        top: Starting directory path
        topdown: If True, do a topdown traversal; if False, do a bottom-up traversal
        onerror: Optional function to handle errors
        followlinks: If True, follow symbolic links
        
    Yields:
        A 3-tuple: (dirpath, dirnames, filenames) - same format as os.walk()
    """
    if not topdown:
        raise ValueError("topdown must be True")

    def load_gitignore(directory: str) -> PathSpec:
        """Load .gitignore patterns from the given directory and its parents."""
        patterns = []
        current_dir = Path(directory)
        
        while True:
            gitignore_path = current_dir / '.gitignore'
            if gitignore_path.is_file():
                with open(gitignore_path, 'r') as f:
                    patterns.extend(f.readlines())
            
            if current_dir.parent == current_dir:
                break
            current_dir = current_dir.parent
        
        return PathSpec.from_lines(GitWildMatchPattern, patterns)
    
    try:
        walk_generator = os.walk(top, topdown, onerror, followlinks)
        
        for dirpath, dirnames, filenames in walk_generator:
            gitignore = load_gitignore(dirpath)
            rel_dirpath = os.path.relpath(dirpath, top)
            if rel_dirpath == '.':
                rel_dirpath = ''
                
            filtered_dirs = []
            for dirname in dirnames:
                rel_path = os.path.join(rel_dirpath, dirname) if rel_dirpath else dirname
                if not gitignore.match_file(rel_path + '/'):
                    filtered_dirs.append(dirname)
            
            filtered_files = []
            for filename in filenames:
                rel_path = os.path.join(rel_dirpath, filename) if rel_dirpath else filename
                if not gitignore.match_file(rel_path):
                    filtered_files.append(filename)
            
            dirnames[:] = filtered_dirs
            yield dirpath, filtered_dirs, filtered_files
            
    except Exception as e:
        if onerror is not None:
            onerror(e)
        else:
            raise
