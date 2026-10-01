// Exporta el contenido editorial de la plataforma Node original (blog, sectores, guías, proceso)
// a data/platform.json para que el generador estático lo use. Uso: node tools/export_platform.js [ruta_plataforma]
const fs = require('fs'), path = require('path'), Module = require('module');
const SRC = path.resolve(process.argv[2] || path.join(process.env.HOME, 'dispron-src'));
const stub = { GALLERY: [], SERVICES: [], SECTORES: [], GUIAS: [], PROCESO: [] };
const load = Module._load;
Module._load = function (req, parent, ...rest) {
  if (req === './data' && parent && parent.filename.startsWith(SRC) && parent.filename.endsWith('blogs-seed.js')) return stub;
  return load.call(this, req, parent, ...rest);
};
const { POSTS } = require(path.join(SRC, 'blogs-seed.js'));
const src = fs.readFileSync(path.join(SRC, 'data.js'), 'utf8');
const grab = (name) => { const m = src.match(new RegExp(`const ${name} = (\\[[\\s\\S]*?\\n\\]);`)) || src.match(new RegExp(`const ${name} = (\\[.*\\]);`)); return Function(`return ${m[1]}`)(); };
const out = { posts: POSTS, sectores: grab('SECTORES'), guias: grab('GUIAS'), proceso: grab('PROCESO'), provincias: grab('PROVINCIAS') };
fs.writeFileSync(path.join(__dirname, '..', 'data', 'platform.json'), JSON.stringify(out, null, 1));
console.log(`OK: ${out.posts.length} artículos, ${out.sectores.length} sectores, ${out.guias.length} guías`);
