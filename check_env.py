#!/usr/bin/env python3
"""
检查Python环境和sys.path
"""

import sys

def main():
    print('Virtual environment:', hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    print('Python executable:', sys.executable)
    print('sys.path:')
    for path in sys.path:
        print(f'  - {path}')
    
    # 尝试导入bs4
    try:
        import bs4
        print('\nbs4 module found:', bs4.__file__)
        print('bs4 version:', bs4.__version__)
    except ImportError as e:
        print('\nbs4 module not found:', e)

if __name__ == '__main__':
    main()
