const menu = document.querySelector('.menu');
const navigation = document.querySelector('#navigation');
function setMenu(open){
 menu.setAttribute('aria-expanded',String(open));
 navigation.classList.toggle('open',open);
 menu.textContent=t(open?'Close':'Menu');
}
menu.addEventListener('click',()=>setMenu(menu.getAttribute('aria-expanded')!=='true'));
navigation.querySelectorAll('a').forEach(link=>link.addEventListener('click',()=>setMenu(false)));
document.addEventListener('keydown',event=>{
 if(event.key==='Escape' && menu.getAttribute('aria-expanded')==='true'){setMenu(false);menu.focus();}
});
document.addEventListener('pointerdown',event=>{
 if(!event.target.closest('header'))setMenu(false);
});
document.querySelector('header').addEventListener('focusout',event=>{
 if(event.relatedTarget && !event.currentTarget.contains(event.relatedTarget))setMenu(false);
});
window.matchMedia('(max-width:860px)').addEventListener('change',()=>setMenu(false));
document.addEventListener('sisi:language-change',()=>setMenu(false));
setMenu(false);
const interest = document.querySelector('#interest');
function updateFields(){document.querySelector('#event-fields').hidden = interest.value !== 'A performance';}
interest.addEventListener('change', updateFields);
document.querySelectorAll('[data-interest]').forEach(link => link.addEventListener('click', () => {interest.value=link.dataset.interest;updateFields();}));
document.querySelector('#enquiry').addEventListener('submit', event => {
 event.preventDefault(); const data = new FormData(event.target);
 const recipient = data.get('interest') === 'A performance' ? 'bookings.sisi@gmail.com' : 'sara.tovsak@gmail.com';
 const body = [t('Hello Sara,'), '', t('I am interested in')+': '+t(data.get('interest')), t('Full name')+': '+data.get('name'), t('Email')+': '+data.get('email'), t('Phone')+': '+(data.get('phone')||t('Not provided')), ...(data.get('interest')==='A performance'?[t('Event date')+': '+(data.get('date')||t('To be confirmed')),t('Event location')+': '+(data.get('location')||t('To be confirmed'))]:[]), '', t('Your wishes')+':', data.get('wishes')].join('\n');
 window.location.href='mailto:'+recipient+'?subject='+encodeURIComponent(t('SISI enquiry')+' — '+t(data.get('interest')))+'&body='+encodeURIComponent(body);
 const status=document.querySelector('#form-status');status.hidden=false;status.textContent=t('Your enquiry is ready in your email app. Please press send there to complete it. If your app did not open, email')+' '+recipient+' '+t('directly.');

});

// Prepare one alpha mask from the original artwork. WebKit must not interpret
// the opaque black background as part of the signature during compositing.
const signatureAsset = (async () => {
 const source = new Image();
 source.src = 'sisi-logo.png';
 await source.decode();
 const canvas = document.createElement('canvas');
 canvas.width = source.naturalWidth; canvas.height = source.naturalHeight;
 const context = canvas.getContext('2d', {willReadFrequently:true});
 context.drawImage(source, 0, 0);
 const pixels = context.getImageData(0, 0, canvas.width, canvas.height);
 for(let i=0;i<pixels.data.length;i+=4){
  const luminance=.2126*pixels.data[i]+.7152*pixels.data[i+1]+.0722*pixels.data[i+2];
  pixels.data[i+3]=Math.round(pixels.data[i+3]*luminance/255);
  pixels.data[i]=pixels.data[i+1]=pixels.data[i+2]=255;
 }
 context.putImageData(pixels, 0, 0);
 const url = canvas.toDataURL('image/png');
 const ready = new Image(); ready.src = url; await ready.decode();
 document.documentElement.style.setProperty('--signature-image', `url("${url}")`);
 document.documentElement.classList.add('signature-ready');
 return url;
})();
// Keep the original artwork visible if image preparation is unavailable.
signatureAsset.catch(() => document.documentElement.classList.add('signature-fallback'));

// Reveal the original signature through sequential strokes, then place it.
(async function signatureEntrance(){
 const intro=document.querySelector('.brand-intro');
 const wrap=intro.querySelector('.intro-logo-wrap');
 const ink=intro.querySelector('.intro-logo');
 const motion=window.matchMedia('(prefers-reduced-motion: reduce)');
 if(motion.matches || window.scrollY>80 || !Element.prototype.animate){intro.remove();return;}
 let finished=false;const animations=[];const flights=[];
 const glintWrap=document.createElement('span');glintWrap.className='signature-glint-wrap';const glint=document.createElement('span');glint.className='signature-glint';glintWrap.append(glint);wrap.append(glintWrap);
 const finish=()=>{if(finished)return;finished=true;animations.forEach(a=>a.cancel());flights.forEach(el=>el.remove());document.documentElement.classList.remove('signature-intro-active');intro.remove();document.dispatchEvent(new Event('sisi:hero-reveal'));clearTimeout(failsafe);['pointerdown','focusin','wheel','touchstart'].forEach(type=>document.removeEventListener(type,finish));window.removeEventListener('resize',finish);motion.removeEventListener('change',finish);};
 const failsafe=setTimeout(finish,7000);
 document.documentElement.classList.add('signature-intro-active');
 ['pointerdown','focusin','wheel','touchstart'].forEach(type=>document.addEventListener(type,finish,{passive:true}));window.addEventListener('resize',finish);motion.addEventListener('change',finish);
 try{
  const signatureURL=await signatureAsset;if(finished)return;
  const shineScaleX=wrap.clientWidth/1440,shineScaleY=wrap.clientHeight/1080;
  for(const path of ink.querySelectorAll('path')){
   const draw=path.animate([{strokeDashoffset:'1'},{strokeDashoffset:'0'}],{duration:Number(path.dataset.duration),easing:'ease-in-out',fill:'forwards'});animations.push(draw);
   // Sample the pen path once. The browser animates a small glow with only
   // transform/opacity, avoiding full-logo gradient and filter repaints per frame.
   const length=path.getTotalLength();
   const shineFrames=Array.from({length:61},(_,index)=>{
    const progress=index/60,point=path.getPointAtLength(length*progress);
    return {offset:progress,transform:`translate3d(${point.x*shineScaleX-4}px,${point.y*shineScaleY-4}px,0)`,opacity:Math.min(1,progress*12)*(progress>.9?(1-progress)*10:1)};
   });
   const shine=glint.animate(shineFrames,{duration:Number(path.dataset.duration),easing:'ease-in-out',fill:'forwards'});
   animations.push(shine);
   await draw.finished;if(finished)return;
   shine.cancel();
  }
  // The final original mask guarantees the complete, crisp mark before flight.
  ink.style.background='#fff';glintWrap.remove();
  if(window.matchMedia('(min-width: 861px) and (hover: hover) and (pointer: fine)').matches){
  // Glow a separate, completed image: only opacity animates, so the writing
  // strokes never have to be blurred and repainted on every frame.
  const glow=document.createElement('img');glow.src=signatureURL;glow.alt='';
  glow.className='signature-completion-glow';glow.setAttribute('aria-hidden','true');
  await glow.decode();if(finished)return;wrap.append(glow);
  const pulse=glow.animate([
   {opacity:0,offset:0},{opacity:.95,offset:.38},
   {opacity:.75,offset:.64},{opacity:0,offset:1}
  ],{duration:850,easing:'ease-in-out',fill:'forwards'});
  animations.push(pulse);await pulse.finished;if(finished)return;glow.remove();
  }else{
   const hold=wrap.animate([{opacity:1},{opacity:1}],{duration:180});
   animations.push(hold);await hold.finished;if(finished)return;
  }
  const from=wrap.getBoundingClientRect();
  const targets=[document.querySelector('.brand>.logo-mask'),document.querySelector('.hero-signature')];
  const landing=targets.map((target,index)=>{
   const to=target.getBoundingClientRect();const copy=document.createElement('img');copy.src=signatureURL;copy.alt='';copy.className='signature-flight';copy.setAttribute('aria-hidden','true');Object.assign(copy.style,{left:from.left+'px',top:from.top+'px',width:from.width+'px',height:from.height+'px'});document.body.append(copy);flights.push(copy);
   const dx=to.left+to.width/2-(from.left+from.width/2);const dy=to.top+to.height/2-(from.top+from.height/2);const scale=Math.min(target.offsetWidth/from.width,target.offsetHeight/from.height);const rotation=index===1?'-8deg':'0deg';
   const flight=copy.animate([{transform:'translate(0,0) scale(1) rotate(0deg)',opacity:1},{transform:`translate(${dx}px,${dy}px) scale(${scale}) rotate(${rotation})`,opacity:index===1?.9:1}],{duration:1100,delay:index*80,easing:'cubic-bezier(.65,0,.2,1)',fill:'forwards'});animations.push(flight);return flight.finished;
  });
  wrap.style.display='none';document.dispatchEvent(new Event('sisi:hero-reveal'));const fade=intro.animate([{opacity:1},{opacity:0}],{duration:800,easing:'ease-in-out',fill:'forwards'});animations.push(fade);
  await Promise.all(landing);finish();
 }catch{finish();}
})();

// Let one performance play at a time so sound never overlaps.
const performanceVideos = [...document.querySelectorAll('.performance-gallery video')];
performanceVideos.forEach(video => video.addEventListener('play', () => {performanceVideos.forEach(other => {if(other !== video) other.pause();});}));

// Enhance native videos with accessible film covers; native controls remain the fallback.
performanceVideos.forEach(video => {
 const film=video.closest('.performance-film');
 const cover=film.querySelector('.film-cover');
 video.controls=false; cover.hidden=false;
 const reveal=()=>{film.classList.add('is-started');cover.hidden=true;video.controls=true;};
 video.addEventListener('play',reveal);
 cover.addEventListener('click',async()=>{
  reveal();
  video.tabIndex=0;video.focus({preventScroll:true});
  try{await video.play();}catch{video.controls=true;}
 });
 video.addEventListener('ended',()=>{film.classList.remove('is-started');cover.hidden=false;video.controls=false;});
});

// Consistent, one-time scroll entrances throughout the page.
(()=>{
 const motion=window.matchMedia('(prefers-reduced-motion: reduce)');
 if(motion.matches || !('IntersectionObserver' in window) || !Element.prototype.animate)return;
 const active=new Map();
 const targets=new Map();
 const groups=[
  '.services .section-head',
  '.services .service-list > details',
  '.highlights-copy > *',
  '.performance-gallery figcaption',
  '.about > .about-label, .about > .about-story',
  '.vision > *',
  '.process .section-head',
  '.process .steps > article',
  '.pricing > div',
  '.contact-intro > *',
  '#enquiry',
  'footer > *'
 ];
 groups.forEach(selector=>document.querySelectorAll(selector).forEach((element,index)=>targets.set(element,index)));
 const observer=new IntersectionObserver(entries=>{
  entries.forEach(entry=>{
   if(!entry.isIntersecting)return;
   const element=entry.target;
   observer.unobserve(element);
   // Never fade already-visible content back out after a fast scroll or anchor jump.
   if(motion.matches || element.contains(document.activeElement) || entry.boundingClientRect.top<window.innerHeight*.8)return;
   const desktop=window.matchMedia('(min-width: 701px)').matches;
   const animation=element.animate([
    {opacity:.55,transform:'translate3d(0,10px,0)'},
    {opacity:1,transform:'translate3d(0,0,0)'}
   ],{duration:500,delay:desktop?Math.min(targets.get(element)*45,90):0,easing:'cubic-bezier(.2,.7,.3,1)',fill:'backwards'});
   active.set(element,animation);
   animation.finished.then(()=>active.delete(element),()=>active.delete(element));
  });
 },{threshold:0,rootMargin:'0px 0px 120px 0px'});
 targets.forEach((_,element)=>observer.observe(element));
 // Interaction takes priority over decorative movement, including form popups.
 const settle=event=>active.forEach((animation,element)=>{
  if(element.contains(event.target)){animation.cancel();active.delete(element);}
 });
 document.addEventListener('focusin',settle);
 document.addEventListener('pointerdown',settle,{passive:true});
 motion.addEventListener('change',()=>{
  if(!motion.matches)return;
  observer.disconnect();active.forEach(animation=>animation.cancel());active.clear();
  document.removeEventListener('focusin',settle);document.removeEventListener('pointerdown',settle);
 });
})();

// Branded dropdown and calendar; the native controls remain the no-JS fallback.
(()=>{
 const chevron='<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="m7 10 5 5 5-5" stroke="currentColor" stroke-width="1.5"/></svg>';
 const calendarIcon='<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><rect x="4" y="5" width="16" height="16" rx="2" stroke="currentColor" stroke-width="1.5"/><path d="M8 3v5m8-5v5M4 11h16" stroke="currentColor" stroke-width="1.5"/></svg>';
 const tick='<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="m5 12 4 4L19 6" stroke="currentColor" stroke-width="1.7"/></svg>';
 const pickers=[];
 function setup(field,native,label,icon){
  const wrap=document.createElement('div');wrap.className='picker';
  const trigger=document.createElement('button');trigger.type='button';trigger.className='picker-trigger';trigger.id=native.id+'-trigger';trigger.setAttribute('aria-labelledby',label+' '+native.id+'-value');trigger.setAttribute('aria-expanded','false');
  const value=document.createElement('span');value.id=native.id+'-value';trigger.append(value);trigger.insertAdjacentHTML('beforeend',icon);
  const popup=document.createElement('div');popup.className='picker-popup';popup.id=native.id+'-popup';popup.hidden=true;trigger.setAttribute('aria-controls',popup.id);
  wrap.append(trigger,popup);field.append(wrap);native.classList.add('picker-native');document.getElementById(label).htmlFor=trigger.id;
  const close=(focus=false)=>{popup.hidden=true;trigger.setAttribute('aria-expanded','false');if(focus)trigger.focus();};
  const open=()=>{pickers.forEach(p=>p.close());popup.hidden=false;trigger.setAttribute('aria-expanded','true');};
  wrap.addEventListener('keydown',e=>{if(e.key==='Escape'){e.preventDefault();close(true);}});
  wrap.addEventListener('focusout',event=>{
   // Focus changes inside the popup must not hide it before the click lands.
   if(event.relatedTarget){if(!wrap.contains(event.relatedTarget))close();return;}
   // Browsers may temporarily report body as active during a focus transition.
   setTimeout(()=>{if(!wrap.contains(document.activeElement))close();},0);
  });
  const picker={wrap,trigger,popup,value,close,open};pickers.push(picker);return picker;
 }
 document.addEventListener('pointerdown',e=>pickers.forEach(p=>{if(!p.wrap.contains(e.target))p.close();}));
 const select=document.getElementById('interest');
 const choice=setup(document.getElementById('interest-field'),select,'interest-label',chevron);
 choice.trigger.setAttribute('aria-haspopup','listbox');choice.popup.setAttribute('role','listbox');choice.popup.setAttribute('aria-labelledby','interest-label');
 const options=[...select.options].map(option=>{
  const button=document.createElement('button');button.type='button';button.className='interest-option';button.setAttribute('role','option');button.dataset.value=option.value;button.textContent=option.text;
  button.addEventListener('click',()=>{select.value=option.value;syncChoice();select.dispatchEvent(new Event('input',{bubbles:true}));select.dispatchEvent(new Event('change',{bubbles:true}));choice.close(true);});choice.popup.append(button);return button;
 });
 function syncChoice(){choice.value.textContent=t(select.value);options.forEach(button=>{const selected=button.dataset.value===select.value;button.setAttribute('aria-selected',String(selected));button.tabIndex=selected?0:-1;button.innerHTML='';button.append(document.createTextNode(t(button.dataset.value)));if(selected)button.insertAdjacentHTML('beforeend',tick);});}
 syncChoice();select.addEventListener('change',()=>{syncChoice();if(select.value!=='A performance')pickers[1]?.close();});
 document.querySelectorAll('[data-interest]').forEach(link=>link.addEventListener('click',syncChoice));
 function openChoice(){choice.open();options[select.selectedIndex].focus();}
 choice.trigger.addEventListener('click',()=>choice.popup.hidden?openChoice():choice.close());
 choice.trigger.addEventListener('keydown',e=>{if(['ArrowDown','ArrowUp'].includes(e.key)){e.preventDefault();openChoice();}});
 choice.popup.addEventListener('keydown',e=>{let index=options.indexOf(document.activeElement);if(e.key==='ArrowDown')index=(index+1)%options.length;else if(e.key==='ArrowUp')index=(index+options.length-1)%options.length;else if(e.key==='Home')index=0;else if(e.key==='End')index=options.length-1;else return;e.preventDefault();options.forEach((b,i)=>b.tabIndex=i===index?0:-1);options[index].focus();});
 const input=document.getElementById('event-date');
 const date=setup(document.getElementById('date-field'),input,'date-label',calendarIcon);
 date.trigger.setAttribute('aria-haspopup','dialog');date.popup.classList.add('calendar-popup');date.popup.setAttribute('role','dialog');date.popup.setAttribute('aria-label','Choose event date');
 const localISO=d=>[d.getFullYear(),String(d.getMonth()+1).padStart(2,'0'),String(d.getDate()).padStart(2,'0')].join('-');
 const parse=s=>{const [y,m,d]=s.split('-').map(Number);return new Date(y,m-1,d,12);};
 const today=new Date();let cursor=input.value?parse(input.value):new Date();
 let display=new Intl.DateTimeFormat(siteLocale(),{day:'numeric',month:'long',year:'numeric'});
 let monthDisplay=new Intl.DateTimeFormat(siteLocale(),{month:'long',year:'numeric'});
 const syncDate=()=>{date.value.textContent=input.value?display.format(parse(input.value)):t('Select a date');};syncDate();input.addEventListener('change',syncDate);
 date.popup.innerHTML='<div class="calendar-heading"><span class="calendar-month" aria-live="polite"></span><div class="calendar-nav"><button type="button" aria-label="Previous month">‹</button><button type="button" aria-label="Next month">›</button></div></div><div class="calendar-week" aria-hidden="true">'+['M','T','W','T','F','S','S'].map(d=>'<span>'+d+'</span>').join('')+'</div><div class="calendar-days" role="group" aria-label="Days"></div><div class="calendar-footer"><button type="button">Clear date</button><button type="button">Today</button></div>';
 const days=date.popup.querySelector('.calendar-days');
 function choose(d){input.value=d?localISO(d):'';syncDate();input.dispatchEvent(new Event('input',{bubbles:true}));input.dispatchEvent(new Event('change',{bubbles:true}));date.close(true);}
 function render(focus=false){
  date.popup.querySelector('.calendar-month').textContent=monthDisplay.format(cursor);days.replaceChildren();
  const y=cursor.getFullYear(),m=cursor.getMonth(),offset=(new Date(y,m,1).getDay()+6)%7,count=new Date(y,m+1,0).getDate();
  for(let i=0;i<offset;i++){const blank=document.createElement('span');blank.setAttribute('aria-hidden','true');days.append(blank);}
  for(let day=1;day<=count;day++){
   const d=new Date(y,m,day,12),iso=localISO(d),button=document.createElement('button');button.type='button';button.className='calendar-day';button.textContent=day;button.dataset.date=iso;button.setAttribute('aria-label',display.format(d));button.setAttribute('aria-pressed',String(iso===input.value));button.tabIndex=day===cursor.getDate()?0:-1;
   if(iso===localISO(today)){button.classList.add('is-today');button.setAttribute('aria-current','date');}
   button.addEventListener('click',()=>choose(d));days.append(button);
  }
  if(focus)days.querySelector('[tabindex="0"]').focus();
 }
 function shiftMonth(amount){const day=cursor.getDate();cursor.setDate(1);cursor.setMonth(cursor.getMonth()+amount);cursor.setDate(Math.min(day,new Date(cursor.getFullYear(),cursor.getMonth()+1,0).getDate()));}
 const nav=date.popup.querySelectorAll('.calendar-nav button');nav.forEach((b,i)=>b.addEventListener('click',()=>{shiftMonth(i===0?-1:1);render();}));
 const foot=date.popup.querySelectorAll('.calendar-footer button');foot[0].addEventListener('click',()=>choose(null));foot[1].addEventListener('click',()=>choose(new Date()));
 days.addEventListener('keydown',e=>{
  if(!e.target.dataset.date)return;cursor=parse(e.target.dataset.date);
  const offsets={ArrowLeft:-1,ArrowRight:1,ArrowUp:-7,ArrowDown:7};
  if(e.key in offsets)cursor.setDate(cursor.getDate()+offsets[e.key]);
  else if(e.key==='Home')cursor.setDate(cursor.getDate()-(cursor.getDay()+6)%7);
  else if(e.key==='End')cursor.setDate(cursor.getDate()+6-(cursor.getDay()+6)%7);
  else if(e.key==='PageUp'||e.key==='PageDown')shiftMonth(e.key==='PageUp'?-1:1);
  else return;e.preventDefault();render(true);
 });
 function localizePickers(){
  display=new Intl.DateTimeFormat(siteLocale(),{day:'numeric',month:'long',year:'numeric'});
  monthDisplay=new Intl.DateTimeFormat(siteLocale(),{month:'long',year:'numeric'});
  syncChoice();syncDate();
  date.popup.setAttribute('aria-label',t('Choose event date'));
  nav[0].setAttribute('aria-label',t('Previous month'));nav[1].setAttribute('aria-label',t('Next month'));
  days.setAttribute('aria-label',t('Days'));
  foot[0].textContent=t('Clear date');foot[1].textContent=t('Today');
  const weekdays=siteLanguage==='sl'?['P','T','S','Č','P','S','N']:['M','T','W','T','F','S','S'];
  date.popup.querySelectorAll('.calendar-week span').forEach((span,i)=>span.textContent=weekdays[i]);
  if(!date.popup.hidden)render();
 }
 document.addEventListener('sisi:language-change',localizePickers);localizePickers();
 date.trigger.addEventListener('click',()=>{if(!date.popup.hidden){date.close();return;}cursor=input.value?parse(input.value):new Date();date.open();render(true);});
})();

// A cinematic headline entrance, timed to the signature backdrop clearing.
(()=>{
 const hero=document.querySelector('.hero');
 const title=hero.querySelector('h1');
 const motion=window.matchMedia('(prefers-reduced-motion: reduce)');
 if(motion.matches || !Element.prototype.animate)return;
 let started=false;const animations=[];
 const settle=()=>animations.forEach(animation=>animation.cancel());
 const reveal=()=>{
  if(started)return;started=true;
  document.removeEventListener('sisi:hero-reveal',reveal);
  if(motion.matches || hero.getBoundingClientRect().bottom<=0)return;
  animations.push(title.animate([
   {opacity:0,transform:'translateY(14px) scale(.92)'},
   {opacity:1,transform:'translateY(0) scale(1)'}
  ],{duration:1500,easing:'cubic-bezier(.16,1,.3,1)',fill:'backwards'}));
  const supporting=[hero.querySelector('.hero-copy .eyebrow'),hero.querySelector('.hero-intro'),hero.querySelector('.actions')];
  supporting.forEach((element,index)=>animations.push(element.animate([
   {opacity:0,transform:'translateY(10px)'},
   {opacity:1,transform:'translateY(0)'}
  ],{duration:900,delay:200+index*170,easing:'cubic-bezier(.2,.7,.3,1)',fill:'backwards'})));
 };
 document.addEventListener('sisi:hero-reveal',reveal);
 if(!document.documentElement.classList.contains('signature-intro-active'))reveal();
 hero.addEventListener('focusin',settle);
 hero.addEventListener('pointerdown',settle,{passive:true});
 motion.addEventListener('change',()=>{if(motion.matches)settle();});
})();

// Prepare still images ahead of the viewport without loading video files.
(()=>{
 if(!('IntersectionObserver' in window))return;
 const images=new IntersectionObserver(entries=>entries.forEach(entry=>{
  if(!entry.isIntersecting)return;
  const img=entry.target;images.unobserve(img);img.loading='eager';
  if(img.decode)img.decode().catch(()=>{});
 }),{rootMargin:'600px 0px',threshold:0});
 document.querySelectorAll('.film-cover img,.about-portrait img').forEach(img=>{img.decoding='async';images.observe(img);});
})();
