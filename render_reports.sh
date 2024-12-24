# Check for pandoc

set -xe

echo $PWD

if ! [ -x "$(command -v pandoc)" ]; then
  echo 'Error: pandoc is not installed.' >&2
  exit 1
fi

pandoc -f markdown -t html -o reports/description.html reports/description.md  --mathml --embed-resources=true

pandoc -f ipynb -t html  exploration.ipynb -o reports/exploration.md   --embed-resources=true

pandoc -s reports/description.html reports/exploration.html -o reports/REPORT.html --css reports/styling.css  --mathml --embed-resources=true --metadata title="Wikipedia recommender system"

pandoc -f html -t markdown -o reports/REPORT.md reports/REPORT.html

ln -s README.md reports/README.md

