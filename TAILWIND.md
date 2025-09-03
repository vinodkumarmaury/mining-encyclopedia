Tailwind setup

This project currently uses Bootstrap for the UI. A Tailwind build pipeline is scaffolded so you can progressively migrate templates.

Steps to build Tailwind locally (Windows PowerShell):

1. Install Node.js (>=16) and npm.
2. From the project root, install Tailwind as a dev dependency:

   npm install -D tailwindcss postcss autoprefixer
   npx tailwindcss init

3. Build once:

   npm run tailwind:build

4. Or run in watch mode while developing:

   npm run tailwind:watch

The output file is written to `static/css/tailwind.css`. You can include it in your templates alongside or instead of `static/css/custom.css`.

Notes:
- The Tailwind pipeline uses `tailwind.config.js` we added to the repo. Adjust `content` paths if you move templates.
- We did not convert templates to Tailwind classes automatically; do that incrementally.
