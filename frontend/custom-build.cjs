const fs = require('fs');
const path = require('path');

const hrmsAppPath = path.resolve(__dirname, '../../hrms/frontend');
const overrideSrcPath = path.resolve(__dirname, './src');
const overridePublicPath = path.resolve(__dirname, './public');
const overrideFilesPath = path.resolve(__dirname, './src_override');

console.log('Starting: Copying original HRMS src, public and root files...');
fs.cpSync(path.join(hrmsAppPath, 'src'), overrideSrcPath, { recursive: true, force: true });
fs.cpSync(path.join(hrmsAppPath, 'public'), overridePublicPath, { recursive: true, force: true });

const rootFiles = ['index.html', 'tailwind.config.js', 'postcss.config.js', 'jsconfig.json', 'ionic.config.json'];
rootFiles.forEach(file => {
    const src = path.join(hrmsAppPath, file);
    const dest = path.join(__dirname, file);
    if (fs.existsSync(src)) {
        fs.cpSync(src, dest, { force: true });
    }
});

console.log('Completed: Copying original HRMS src, public and root files.');

console.log('Starting: Applying fonzel overrides...');
fs.cpSync(overrideFilesPath, overrideSrcPath, { recursive: true, force: true });
console.log('Completed: Applying fonzel overrides.');

console.log('Starting: Copying HRMS python context files...');
const hrmsWwwPath = path.resolve(__dirname, '../../hrms/hrms/www');
const fonzelWwwPath = path.resolve(__dirname, '../fonzel/www');

const wwwFiles = ['hrms.py', 'roster.py'];
wwwFiles.forEach(file => {
    const src = path.join(hrmsWwwPath, file);
    const dest = path.join(fonzelWwwPath, file);
    if (fs.existsSync(src)) {
        fs.mkdirSync(path.dirname(dest), { recursive: true });
        fs.cpSync(src, dest, { force: true });
    }
});
console.log('Completed: Copying HRMS python context files.');
