# Check for pandoc

if ! [ -x "$(command -v pandoc)" ]; then
  echo 'Error: pandoc is not installed.' >&2
  exit 1
fi

# pandoc -s -f markdown -t html -o reports/README.html README.md --filter pandoc-include --mathjax --css=reports/styling.css --metadata title="Wikipedia search engine"

pandoc -s exploration.ipynb -o reports/exploration.html  --metadata title="Exploration"


# jupyter nbconvert --to html exploration.ipynb --output-dir=reports --output exploration.html

