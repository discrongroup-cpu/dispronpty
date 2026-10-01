const fs = require('fs');
const path = require('path');

const d = JSON.parse(fs.readFileSync(path.join(__dirname, 'site-data.json'), 'utf8'));
module.exports = {
  SERVICES: d.SERVICES, SECTORES: d.SECTORES, GUIAS: d.GUIAS, PROCESO: d.PROCESO,
  PROVINCIAS: d.PROVINCIAS, CONTACT: d.CONTACT, GALLERY: d.GALLERY, PATHS: d.PATHS, KEYWORDS: d.KEYWORDS,
};
