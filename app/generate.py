#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from html_generator import HTMLGenerator
import sys

def main():
    try:
        template_path = sys.argv[1] if len(sys.argv) > 1 else 'template.html'
        output_path = sys.argv[2] if len(sys.argv) > 2 else 'index.html'
        
        generator = HTMLGenerator(
            db_path='sites.db',
            template_path=template_path,
            output_path=output_path
        )
        generator.generate_html()
        
    except Exception as e:
        print(f"Ошибка: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())