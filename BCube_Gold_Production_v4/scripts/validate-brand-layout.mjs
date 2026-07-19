#!/usr/bin/env node
import fs from 'node:fs';
import crypto from 'node:crypto';
const [evidenceFile, mascotFile] = process.argv.slice(2);
if (!evidenceFile || !mascotFile) process.exit(2);
const e=JSON.parse(fs.readFileSync(evidenceFile,'utf8'));
const intersect=(a,b)=>a.x < b.x+b.width && a.x+a.width > b.x && a.y < b.y+b.height && a.y+a.height > b.y;
const failures=[];
if(intersect(e.logo_protected_zone,e.subheader_bbox)) failures.push('subheader intersects protected logo zone');
const hash=crypto.createHash('sha256').update(fs.readFileSync(mascotFile)).digest('hex');
if(e.official_mascot_required && e.official_mascot_sha256!==hash) failures.push('mascot is not the locked approved asset');
if(e.official_mascot_required && e.mascot_status!=='PASS') failures.push('mascot visual review missing');
if(e.corner_template!=='LOCKED_PALE_YELLOW_QUARTER_CIRCLE') failures.push('top-right corner is not the locked template');
if(e.generated_template_regions_removed!==true) failures.push('generated header/corner/mascot regions were not removed');
if(failures.length){console.error('REJECTED: '+failures.join('; '));process.exit(1)}
console.log('PASS: logo clearance and approved mascot identity verified.');
