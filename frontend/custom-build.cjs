const fs = require('fs-extra');
const path = require('path');

const hrmsAppPath = path.resolve(__dirname, '../../hrms/frontend');
const overrideSrcPath = path.resolve(__dirname, './src');
const overridePublicPath = path.resolve(__dirname, './public');
const overrideFilesPath = path.resolve(__dirname, './src_override');

console.log('Starting: Copying original HRMS src, public and root files...');
fs.copySync(path.join(hrmsAppPath, 'src'), overrideSrcPath);
fs.copySync(path.join(hrmsAppPath, 'public'), overridePublicPath);

const rootFiles = ['index.html', 'tailwind.config.js', 'postcss.config.js', 'jsconfig.json', 'ionic.config.json'];
rootFiles.forEach(file => {
    const src = path.join(hrmsAppPath, file);
    const dest = path.join(__dirname, file);
    if (fs.existsSync(src)) {
        fs.copySync(src, dest);
    }
});

console.log('Completed: Copying original HRMS src, public and root files.');

console.log('Starting: Applying fonzel overrides...');
fs.copySync(overrideFilesPath, overrideSrcPath);
console.log('Completed: Applying fonzel overrides.');

console.log('Starting: Copying HRMS python context files...');
const hrmsWwwPath = path.resolve(__dirname, '../../hrms/hrms/www');
const fonzelWwwPath = path.resolve(__dirname, '../fonzel/www');

const wwwFiles = ['hrms.py', 'roster.py'];
wwwFiles.forEach(file => {
    const src = path.join(hrmsWwwPath, file);
    const dest = path.join(fonzelWwwPath, file);
    if (fs.existsSync(src)) {
        fs.ensureDirSync(path.dirname(dest));
        fs.copySync(src, dest);
    }
});
console.log('Completed: Copying HRMS python context files.');
