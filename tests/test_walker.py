import os
import tempfile
import shutil
import pytest
from gitwalk import gitwalk

@pytest.fixture
def test_dir():
    """Create a temporary directory for testing"""
    tmp_dir = tempfile.mkdtemp()
    
    # Create test directory structure
    os.makedirs(os.path.join(tmp_dir, "src"))
    os.makedirs(os.path.join(tmp_dir, "tests"))
    os.makedirs(os.path.join(tmp_dir, "build"))
    os.makedirs(os.path.join(tmp_dir, "src/cache"))
    os.makedirs(os.path.join(tmp_dir, "build/nested"))
    
    # Create test files
    open(os.path.join(tmp_dir, "README.md"), "w").close()
    open(os.path.join(tmp_dir, "src/main.py"), "w").close()
    open(os.path.join(tmp_dir, "src/cache/temp.txt"), "w").close()
    open(os.path.join(tmp_dir, "tests/test_main.py"), "w").close()
    open(os.path.join(tmp_dir, "build/output.exe"), "w").close()
    open(os.path.join(tmp_dir, "build/nested/nested.exe"), "w").close()
    
    # Create .gitignore
    with open(os.path.join(tmp_dir, ".gitignore"), "w") as f:
        f.write("""
build/
*.exe
src/cache/
*.pyc
""")
    
    yield tmp_dir
    
    # Cleanup
    shutil.rmtree(tmp_dir)

def test_basic_walk(test_dir):
    """Test basic walking functionality"""
    walked_files = set()
    walked_dirs = set()
    
    for dirpath, dirnames, filenames in gitwalk(test_dir):
        walked_dirs.update(dirnames)
        walked_files.update(filenames)
    
    assert "build" not in walked_dirs
    assert "cache" not in walked_dirs
    assert "nested" not in walked_dirs  # Should not include nested dirs in ignored dirs
    assert "README.md" in walked_files
    assert "main.py" in walked_files
    assert "test_main.py" in walked_files
    assert "output.exe" not in walked_files
    assert "nested.exe" not in walked_files
    assert "temp.txt" not in walked_files

def test_topdown_false_raises_error():
    """Test that setting topdown=False raises ValueError"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        with pytest.raises(ValueError):
            list(gitwalk(tmp_dir, topdown=False))

def test_pattern_walk():
    """Test walking with pattern-based gitignore rules"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create test structure
        os.makedirs(os.path.join(tmp_dir, "docs"))
        os.makedirs(os.path.join(tmp_dir, "src"))
        os.makedirs(os.path.join(tmp_dir, "tests"))
        
        # Create various file types
        open(os.path.join(tmp_dir, "docs/doc1.md"), "w").close()
        open(os.path.join(tmp_dir, "docs/doc2.txt"), "w").close()
        open(os.path.join(tmp_dir, "src/main.py"), "w").close()
        open(os.path.join(tmp_dir, "src/main.pyc"), "w").close()
        open(os.path.join(tmp_dir, "tests/.env"), "w").close()
        open(os.path.join(tmp_dir, "tests/test_main.py"), "w").close()
        
        # Create .gitignore with pattern-based rules
        with open(os.path.join(tmp_dir, ".gitignore"), "w") as f:
            f.write("""
*.pyc
*.txt
.env
!docs/*.txt
""")
        
        walked_files = set()
        for _, _, filenames in gitwalk(tmp_dir):
            walked_files.update(filenames)
        
        # Check pattern matching
        assert "doc1.md" in walked_files  # Regular file, not ignored
        assert "doc2.txt" in walked_files  # Negated by !docs/*.txt
        assert "main.py" in walked_files   # Regular file, not ignored
        assert "main.pyc" not in walked_files  # Ignored by *.pyc
        assert ".env" not in walked_files      # Ignored by .env
        assert "test_main.py" in walked_files  # Regular file, not ignored

def test_nested_gitignore():
    """Test walking with nested .gitignore files"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create nested structure
        os.makedirs(os.path.join(tmp_dir, "frontend"))
        os.makedirs(os.path.join(tmp_dir, "frontend/node_modules"))
        os.makedirs(os.path.join(tmp_dir, "backend"))
        os.makedirs(os.path.join(tmp_dir, "backend/venv"))
        
        # Create test files
        open(os.path.join(tmp_dir, "frontend/app.js"), "w").close()
        open(os.path.join(tmp_dir, "frontend/package.json"), "w").close()
        open(os.path.join(tmp_dir, "frontend/node_modules/dep.js"), "w").close()
        open(os.path.join(tmp_dir, "backend/server.py"), "w").close()
        open(os.path.join(tmp_dir, "backend/requirements.txt"), "w").close()
        open(os.path.join(tmp_dir, "backend/venv/lib.py"), "w").close()
        
        # Create root .gitignore
        with open(os.path.join(tmp_dir, ".gitignore"), "w") as f:
            f.write("*.txt\n")
        
        # Create frontend/.gitignore
        with open(os.path.join(tmp_dir, "frontend", ".gitignore"), "w") as f:
            f.write("node_modules/\n")
        
        # Create backend/.gitignore
        with open(os.path.join(tmp_dir, "backend", ".gitignore"), "w") as f:
            f.write("""
venv/
!requirements.txt
""")
        
        walked_files = set()
        walked_dirs = set()

        for _, dirnames, filenames in gitwalk(tmp_dir):
            walked_dirs.update(dirnames)
            walked_files.update(filenames)
        
        # Check nested .gitignore rules
        assert "node_modules" not in walked_dirs  # Ignored by frontend/.gitignore
        assert "venv" not in walked_dirs          # Ignored by backend/.gitignore
        assert "app.js" in walked_files           # Not ignored
        assert "package.json" in walked_files     # Not ignored
        assert "dep.js" not in walked_files       # In ignored directory
        assert "server.py" in walked_files        # Not ignored
        assert "requirements.txt" not in walked_files  # Same behaviour as git
        assert "lib.py" not in walked_files       # In ignored directory

def test_empty_directory():
    """Test handling of empty directories"""
    with tempfile.TemporaryDirectory() as empty_dir:
        results = list(gitwalk(empty_dir))
        assert len(results) == 1
        assert results[0][1] == []
        assert results[0][2] == []
