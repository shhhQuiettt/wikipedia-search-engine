# Check for pandoc

if ! [ -x "$(command -v pandoc)" ]; then
  echo 'Error: pandoc is not installed.' >&2
  exit 1
fi

pandoc -s -f markdown -t html -o reports/report.html README.md --filter pandoc-include --mathjax --css=reports/styling.css --metadata title="Wikipedia search engine"


