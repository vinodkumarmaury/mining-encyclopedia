const fs = require('fs');
const path = require('path');
const tailwind = require('tailwindcss');
const postcss = require('postcss');

const inputPath = path.resolve(__dirname, '../assets/css/tailwind_input.css');
const outputPath = path.resolve(__dirname, '../static/css/tailwind.css');

const tailwindConfig = require(path.resolve(__dirname, '../tailwind.config.js'));

async function build() {
  const inputCss = fs.readFileSync(inputPath, 'utf8');
  const processor = postcss([tailwind(tailwindConfig)]);
  const result = await processor.process(inputCss, { from: inputPath, to: outputPath });
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, result.css);
  console.log('Wrote', outputPath);
}

build().catch(err => { console.error(err); process.exit(1); });
