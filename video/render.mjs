// Renderiza kosgroup.html a vídeo fotograma a fotograma (determinista) y lo codifica con ffmpeg.
// Uso (desde video/):  npm ci  &&  node render.mjs
// Variables opcionales: FPS (30), CHROME (ruta a Chrome/Chromium), FFMPEG (ruta a ffmpeg).
// Salida: ../site/media/kosgroup.mp4 (H.264), kosgroup.webm (VP9) y kosgroup-poster.jpg.
import { chromium } from 'playwright-core';
import { mkdirSync, rmSync, existsSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';

const here = path.dirname(fileURLToPath(import.meta.url));
const FPS = Number(process.env.FPS || 30);
const CHROME = process.env.CHROME || 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const FFMPEG = process.env.FFMPEG || 'ffmpeg';
const frames = path.join(here, '.frames');
const out = path.join(here, '..', 'site', 'media');
const POSTER_MS = 7600; // fotograma del claim

rmSync(frames, { recursive: true, force: true });
mkdirSync(frames, { recursive: true });
mkdirSync(out, { recursive: true });

const browser = await chromium.launch({ executablePath: existsSync(CHROME) ? CHROME : undefined, args: ['--force-device-scale-factor=1'] });
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
await page.goto(pathToFileURL(path.join(here, 'kosgroup.html')).href, { waitUntil: 'load' });
await page.evaluate(() => document.fonts.ready);
await page.evaluate(() => Promise.all([...document.images].map(i => i.decode().catch(() => {}))));
const duration = await page.evaluate(() => window.DURATION);
const total = Math.round((duration / 1000) * FPS);
for (let i = 0; i < total; i++) {
  const t = (i * 1000) / FPS;
  await page.evaluate(ms => window.seek(ms), t);
  await page.screenshot({ path: path.join(frames, `f${String(i).padStart(5, '0')}.png`) });
  if (i % FPS === 0) process.stdout.write(`\r${Math.round(t / 1000)}s / ${duration / 1000}s`);
}
await page.evaluate(ms => window.seek(ms), POSTER_MS);
await page.screenshot({ path: path.join(out, 'kosgroup-poster.jpg'), type: 'jpeg', quality: 82 });
await browser.close();
process.stdout.write('\nCodificando...\n');

const input = ['-y', '-framerate', String(FPS), '-i', path.join(frames, 'f%05d.png')];
execFileSync(FFMPEG, [...input, '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-pix_fmt', 'yuv420p',
  '-movflags', '+faststart', path.join(out, 'kosgroup.mp4')], { stdio: 'inherit' });
execFileSync(FFMPEG, [...input, '-c:v', 'libvpx-vp9', '-b:v', '0', '-crf', '34', '-row-mt', '1', '-deadline', 'good',
  '-pix_fmt', 'yuv420p', path.join(out, 'kosgroup.webm')], { stdio: 'inherit' });
rmSync(frames, { recursive: true, force: true });
console.log('Listo:', out);
