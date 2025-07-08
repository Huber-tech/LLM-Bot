find . -type f -name "*.py" \
    -not -path "*/venv/*" \
    -not -path "*/.git/*" \
| sort | while read file; do
    echo "### FILE: $file" >> project_dump.txt
    cat "$file" >> project_dump.txt
    echo -e "\n\n" >> project_dump.txt
done
