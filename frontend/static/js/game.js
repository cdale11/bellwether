const $=id=>document.getElementById(id); let currentGameData=null,requestInFlight=false,pendingTalkNpc=null,activeCategory=null,developerData=null,assetManifest={scenes:{}};

function slugifyLocation(v){return String(v||'').toLowerCase().replace(/[^a-z0-9]+/g,'_').replace(/^_|_$/g,'');}
function applyVisualState(data){
 const s=data.state||{}, w=s.weather||{}, key=slugifyLocation(data.location?.name), entry=assetManifest.scenes?.[key];
 const img=$('scene-art'), stage=$('scene-stage');
 document.body.dataset.season=String(s.season?.label||'').toLowerCase().replace(/\s+/g,'_');
 document.body.dataset.daypart=String(s.daypart||'').toLowerCase();
 if(entry?.default){img.src=entry.default;img.classList.remove('hidden');stage.classList.add('has-art');stage.style.setProperty('--scene-focal',entry.focal||'50% 50%');}
 else{img.removeAttribute('src');img.classList.add('hidden');stage.classList.remove('has-art');stage.style.removeProperty('--scene-focal');}
}
async function loadAssetManifest(){try{const r=await fetch('/static/assets/asset_manifest.json',{cache:'no-store'});if(r.ok)assetManifest=await r.json();}catch(e){console.warn('Asset manifest fallback active',e);}}

const ACTION_CATEGORIES=[['people','People',['story','talk','free_talk','choice']],['activities','Activities',['life','job','economy']],['explore','Explore',['observe']],['investigate','Investigate',['investigate']],['travel','Travel',['travel']]];
function escapeHtml(v){return String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]));}
function devMode(){const q=new URLSearchParams(location.search);if(q.get('dev')==='1')sessionStorage.setItem('bellwether_dev','1');if(q.get('dev')==='0')sessionStorage.removeItem('bellwether_dev');return sessionStorage.getItem('bellwether_dev')==='1';}
function render(data){currentGameData=data;const s=data.state,w=s.weather||{};$('location').textContent=data.location.name;$('scene-title').textContent=data.location.name;$('scene-title-overlay').textContent=data.location.name;const season=s.season?.label||'Season unknown';$('status').textContent=`Day ${s.day} · ${s.time} · ${season} · ${w.label} · ${w.temperature_c}°C · £${s.money}`;document.body.dataset.weather=w.state||'clear';document.body.dataset.daypart=s.daypart||'';applyVisualState(data);
const effect=data.world_context?.weather_effect||'';$('weather-impact').textContent=effect;$('weather-impact').style.display=effect?'block':'none';$('environment-line').textContent=effect||'The village keeps its own quiet rhythm.';$('environment-line-overlay').textContent=effect||'The village keeps its own quiet rhythm.';
const msgs=s.new_messages||[];$('dialogue').innerHTML=msgs.length?msgs.map(l=>`<p class="line"><span class="speaker">${escapeHtml(l.speaker)}</span><br>${escapeHtml(l.text)}</p>`).join(''):'<p class="line quiet-line">The moment settles. Choose what to do next.</p>';$('dialogue').scrollTop=$('dialogue').scrollHeight;
renderActions(data.actions||[]);renderContext(data);$('dev-button').classList.toggle('hidden',!devMode());}
function actionButton(a){const b=document.createElement('button');b.textContent=a.label;b.onclick=()=>a.kind==='free_talk'?openTalk(a):act(a.id);return b;}
function categoryFor(a){for(const [id,,kinds] of ACTION_CATEGORIES)if(kinds.includes(a.kind))return id;return 'activities';}
function renderActions(actions){const groups={};ACTION_CATEGORIES.forEach(([id])=>groups[id]=[]);actions.forEach(a=>groups[categoryFor(a)].push(a));
const quick=actions.filter(a=>a.kind==='choice'||a.kind==='talk'||a.kind==='free_talk'||/water|treat|shelter|begin another run/i.test(a.label));$('quick-actions').innerHTML='';quick.slice(0,4).forEach(a=>$('quick-actions').appendChild(actionButton(a)));
$('action-dock').innerHTML='';ACTION_CATEGORIES.forEach(([id,label])=>{const b=document.createElement('button');b.textContent=`${label}${groups[id].length?` · ${groups[id].length}`:''}`;b.disabled=!groups[id].length;b.onclick=()=>openActionTray(id,label,groups[id]);$('action-dock').appendChild(b);});
if(activeCategory){const meta=ACTION_CATEGORIES.find(x=>x[0]===activeCategory);if(meta)openActionTray(meta[0],meta[1],groups[meta[0]]);}}
function openActionTray(id,label,items){activeCategory=id;$('tray-title').textContent=label;$('tray-actions').innerHTML='';items.forEach(a=>$('tray-actions').appendChild(actionButton(a)));$('action-tray').classList.remove('hidden');}
function closeActionTray(){activeCategory=null;$('action-tray').classList.add('hidden');}
function renderContext(data){const s=data.state;const all=[...(s.quests?.main||[]),...(s.quests?.side||[])];const q=all.find(x=>!x.done);$('current-objective').innerHTML=q?`<strong>${escapeHtml(q.title)}</strong><p>${escapeHtml(q.objective)}</p>`:'<small>No urgent thread. The day is yours.</small>';
const people=(data.present?.npcs||[]).map(n=>{const key=slugifyLocation(n.id||n.name),entry=assetManifest.characters?.[key]||assetManifest.characters?.[slugifyLocation(n.name)],src=entry?.neutral||entry?.default||'';return `<div class="presence npc-presence">${src?`<img class="npc-portrait" src="${escapeHtml(src)}" alt="Portrait of ${escapeHtml(n.name)}">`:''}<div class="npc-presence-copy"><strong>${escapeHtml(n.name)}</strong><br><small>${escapeHtml(n.activity)}</small></div></div>`;});$('presence').innerHTML=people.join('')||'<small>The immediate area is quiet.</small>';
const danger=s.danger||{},job=s.employment||s.jobs||{};$('immediate-state').innerHTML=`<div>${escapeHtml(data.world_context?.weather_effect||'Conditions are ordinary.')}</div>${danger.injuries?.length?`<div class="warning">Injured · ${danger.injuries.length} condition(s)</div>`:''}${job.current_job?`<div>Work: ${escapeHtml(job.current_job)}</div>`:''}`; const sides=(s.quests?.side||[]).filter(x=>!x.done); $('side-stories').innerHTML=sides.map(x=>`<div class="side-story"><strong>${escapeHtml(x.title)}</strong><small>${escapeHtml(x.objective)}</small></div>`).join('')||'<small>No active side stories.</small>'; const hist=(s.history||[]).slice(-4).reverse(); $('recent-events').innerHTML=hist.map(x=>`<div class="recent-event">${escapeHtml(x.text)}</div>`).join('')||'<small>Your days here are only beginning.</small>';}
function relationshipDescription(r){const f=Number(r.familiarity||0),a=Number(r.affinity||0),t=Number(r.trust||0);const familiarity=f>=8?'Well known':f>=4?'A familiar face':'New acquaintance';const warmth=a>=6?'Warm toward you':a>=2?'Comfortable around you':a<0?'Uneasy around you':'Still forming an impression';const trust=t>=6?'Trusts you':t>=2?'Some trust is forming':t<0?'Guarded':'Trust remains cautious';return `${familiarity}<br><small>${warmth} · ${trust}</small>`;}
function availableActions(prefix){return (currentGameData?.actions||[]).filter(a=>a.id.startsWith(prefix));}
function panelActionButtons(items){return items.map(a=>`<button class="panel-action" data-action-id="${escapeHtml(a.id)}">${escapeHtml(a.label)}</button>`).join('');}
function cropName(id){return String(id||'').replace(/_/g,' ').replace(/\b\w/g,c=>c.toUpperCase());}
function gardenHtml(s){const g=s.player_activities?.garden||{},plots=g.plots||[];const plotHtml=plots.map((p,i)=>{if(!p)return `<div class="garden-plot empty"><strong>Plot ${i+1}</strong><span>Empty bed</span></div>`;const ratio=Math.max(0,Math.min(100,Math.round(100*Number(p.growth||0)/Math.max(1,Number(p.growth_required||1)))));return `<div class="garden-plot"><strong>Plot ${i+1} · ${escapeHtml(cropName(p.crop_id))}</strong><span>${ratio>=100?'Ready to harvest':ratio>=70?'Maturing':ratio>=30?'Growing':ratio>0?'Seedling':'Sown'} · ${ratio}%</span><div class="meter"><i style="width:${ratio}%"></i></div><small>Health ${Math.round(Number(p.health??100))}%</small></div>`;}).join('');const seeds=Object.entries(g.seed_stock||{}).filter(([,n])=>Number(n)>0).map(([k,n])=>`${cropName(k)} ×${n}`).join(' · ')||'No seeds stored';const harvest=Object.entries(g.harvest_store||{}).filter(([,n])=>Number(n)>0).map(([k,n])=>`${cropName(k)} ×${n}`).join(' · ')||'Nothing harvested yet';return `<div class="garden-overview"><div class="stat-grid"><div><b>Soil</b><span>${g.soil_prepared?'Prepared':'Unprepared'} · ${Math.round(Number(g.soil_condition||0))}%</span></div><div><b>Moisture</b><span>${Math.round(Number(g.moisture||0))}%</span></div><div><b>Weeds</b><span>${Math.round(Number(g.weeds||0))}%</span></div><div><b>Gardening skill</b><span>${Number(s.player_activities?.skills?.gardening||0)}</span></div></div><div class="garden-plots">${plotHtml}</div><div class="store-line"><b>Seed box</b><span>${escapeHtml(seeds)}</span></div><div class="store-line"><b>Harvest basket</b><span>${escapeHtml(harvest)}</span></div><div class="panel-actions">${panelActionButtons(availableActions('garden:'))}</div></div>`;}
function cookingHtml(s){const c=s.content_progression?.cooking||{},known=c.recipes_known||[];const names={radish_toast:'Radish and butter toast',garden_salad:'Garden salad',carrot_soup:'Carrot soup',bean_stew:'Broad bean stew'};const available=new Set(availableActions('content:cook:').map(a=>a.id.split(':').pop()));return `<div class="recipe-grid">${known.map(id=>`<div class="recipe-card ${available.has(id)?'available':''}"><strong>${escapeHtml(names[id]||cropName(id))}</strong><span>${available.has(id)?'Ingredients ready':'Ingredients needed'}</span></div>`).join('')}</div><p>Meals cooked: <strong>${Number(c.meals_cooked||0)}</strong> · Cooking skill: <strong>${Number(s.player_activities?.skills?.cooking||0)}</strong></p><div class="panel-actions">${panelActionButtons(availableActions('content:cook:'))}</div>`;}
function homeHtml(s){const rest=s.content_progression?.home_restoration||{},done=new Set(rest.completed||[]),repairs={kitchen_stove:'Old kitchen stove',bedroom_window:'Bedroom window',garden_gate:'Garden gate'};return `<div class="home-hero"><img src="/static/assets/scenes/cottage_interior/cottage_interior.png" alt="Ashcroft Cottage interior"><div><h3>Ashcroft Cottage</h3><p>Cottage care ${Number(s.player_life?.cottage_care||0)} · Home-care skill ${Number(s.player_activities?.skills?.home_care||0)}</p></div></div><div class="home-tabs"><button data-home-view="garden">Garden</button><button data-home-view="cooking">Cooking</button><button data-home-view="restoration">Restoration</button></div><div id="home-detail"><h3>Garden</h3>${gardenHtml(s)}</div><template id="home-garden-template">${gardenHtml(s)}</template><template id="home-cooking-template">${cookingHtml(s)}</template><template id="home-restoration-template"><div class="repair-grid">${Object.entries(repairs).map(([id,name])=>`<div class="repair-card ${done.has(id)?'done':''}"><strong>${escapeHtml(name)}</strong><span>${done.has(id)?'Completed':'Still needs attention'}</span></div>`).join('')}</div><p>Repair supplies: <strong>${Number(s.economy?.household?.repair_supplies||0)}</strong></p><div class="panel-actions">${panelActionButtons(availableActions('content:repair:'))}</div></template>`;}
function mapHtml(s){
 const current=currentGameData.location.id;
 const mapState=s.map_exploration||{};
 const discovered=new Set(mapState.discovered_locations||[]); discovered.add(current);
 const discoveredPaths=new Set(mapState.discovered_paths||[]);
 // Coordinates are percentages of the canonical 1536x1024 illustrated map.
 const anchors={
  bus_stop:[25.0,73.5], village_road:[35.5,58.5], bakery:[33.8,39.5],
  village_shop:[30.7,52.0], village_green:[43.2,49.0], churchyard:[51.0,26.0],
  ashcroft_cottage:[41.8,81.0], riverside_path:[13.0,48.0], railway_halt:[18.0,84.0]
 };
 const regions={
  bus_stop:'19,66 31,66 33,78 27,84 18,80 16,72',
  village_road:'27,48 43,45 48,57 42,67 29,66 24,57',
  bakery:'27,32 40,31 43,42 37,48 27,45 24,38',
  village_shop:'24,45 37,44 39,56 33,63 22,59 20,51',
  village_green:'35,40 52,39 57,51 50,61 37,61 32,51',
  churchyard:'42,15 61,14 66,29 59,39 45,38 39,27',
  ashcroft_cottage:'32,70 52,69 56,84 48,94 34,94 27,84',
  riverside_path:'3,32 20,31 25,47 20,65 8,70 2,58',
  railway_halt:'8,75 28,74 31,94 7,95'
 };
 const routePairs={
  'bus_stop::village_road':['bus_stop','village_road'],
  'bakery::village_road':['bakery','village_road'],
  'village_green::village_road':['village_road','village_green'],
  'village_road::village_shop':['village_road','village_shop'],
  'churchyard::village_road':['village_road','churchyard'],
  'churchyard::village_green':['village_green','churchyard'],
  'ashcroft_cottage::village_green':['village_green','ashcroft_cottage'],
  'riverside_path::village_green':['village_green','riverside_path'],
  'railway_halt::riverside_path':['riverside_path','railway_halt']
 };
 const polygons=[...discovered].filter(id=>regions[id]).map(id=>`<polygon points="${regions[id]}"/>`).join('');
 const paths=[...discoveredPaths].map(key=>routePairs[key]).filter(Boolean).map(([a,b])=>{const p1=anchors[a],p2=anchors[b];return `<line x1="${p1[0]}" y1="${p1[1]}" x2="${p2[0]}" y2="${p2[1]}"/>`;}).join('');
 const [cx,cy]=anchors[current]||[50,50];
 return `<div class="exploration-map">
   <div class="map-unknown" aria-hidden="true"></div>
   <svg class="map-revealed" viewBox="0 0 100 100" preserveAspectRatio="none" aria-label="Explored map of Bellwether">
    <defs>
     <filter id="bellwether-feather" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="1.65"/></filter>
     <mask id="bellwether-exploration-mask" maskUnits="userSpaceOnUse" x="0" y="0" width="100" height="100">
      <rect width="100" height="100" fill="black"/>
      <g class="map-mask-shapes" filter="url(#bellwether-feather)" fill="white" stroke="white" stroke-width="8" stroke-linecap="round" stroke-linejoin="round">${paths}${polygons}</g>
      <!-- Decorative reference graphics in the source artwork are never revealed as geography. -->
      <rect x="2.4" y="72.5" width="13.8" height="23.5" fill="black" stroke="none"/>
      <rect x="85.5" y="2.0" width="12.5" height="18.5" fill="black" stroke="none"/>
     </mask>
    </defs>
    <image href="/static/assets/maps/Base_Map.png" x="0" y="0" width="100" height="100" preserveAspectRatio="none" mask="url(#bellwether-exploration-mask)"/>
   </svg>
   <div class="map-paper-grain" aria-hidden="true"></div>
   <img class="map-reference map-compass" src="/static/assets/maps/map_compass.png" alt="North compass rose">
   <img class="map-reference map-legend" src="/static/assets/maps/map_legend.png" alt="Map legend: main road, path, track, river, buildings, woods, fields and water">
   <div class="map-vignette" aria-hidden="true"></div>
   <div class="player-map-marker" style="left:${cx}%;top:${cy}%" aria-label="You are here"><i></i><span>You are here</span></div>
  </div><p class="map-note">Bellwether is drawn into clarity as you travel. Unexplored country remains blank parchment.</p>`;
}

function panelHtml(type){const s=currentGameData.state;if(type==='history')return (s.history||[]).map(l=>`<p class="history-line"><span class="speaker">${escapeHtml(l.speaker)}</span><br>${escapeHtml(l.text)}</p>`).join('')||'<p>No history yet.</p>';
if(type==='journal'){const block=(title,xs)=>`<h3>${title}</h3>`+(xs||[]).map(q=>`<div class="quest ${q.done?'done':''}"><strong>${escapeHtml(q.title)}</strong><br><small>${escapeHtml(q.objective)}</small></div>`).join('');return block('Main Story',s.quests.main)+block('Side Stories',s.quests.side);}
if(type==='inventory'){const harvest=s.player_activities?.garden?.harvest_store||{},house=s.economy?.household||{};return `<h3>Carried</h3><ul>${(s.inventory||[]).map(i=>`<li>${escapeHtml(i)}</li>`).join('')||'<li>Nothing carried</li>'}</ul><h3>Pantry and Household</h3><div class="inventory-grid">${Object.entries(house).filter(([,n])=>Number(n)>0).map(([k,n])=>`<div><strong>${escapeHtml(cropName(k))}</strong><span>×${n}</span></div>`).join('')||'<p>The cupboards are bare.</p>'}</div><h3>Garden Produce</h3><div class="inventory-grid">${Object.entries(harvest).filter(([,n])=>Number(n)>0).map(([k,n])=>`<div><strong>${escapeHtml(cropName(k))}</strong><span>×${n}</span></div>`).join('')||'<p>No produce stored.</p>'}</div><h3>Field Collections</h3><p>Birds recorded: <strong>${Number(s.player_activities?.hobbies?.collections?.birds?.length||0)}</strong> · History notes: <strong>${Number(s.player_activities?.hobbies?.collections?.history_notes?.length||0)}</strong> · Sketches: <strong>${Number(s.player_activities?.hobbies?.collections?.sketches?.length||0)}</strong></p>`;}
if(type==='relationships'){const flags=s.flags||{};return Object.entries(s.relationships||{}).filter(([id,r])=>Number(r.talks||0)>0||(id==='jonah'&&flags.met_jonah)||(id==='mara'&&flags.met_mara)).map(([id,r])=>{const entry=assetManifest.characters?.[id],src=entry?.neutral||'';return `<div class="relationship-card relationship-person">${src?`<img src="${escapeHtml(src)}" alt="Portrait of ${escapeHtml(s.npcs?.[id]?.name||id)}">`:''}<div><h3>${escapeHtml(s.npcs?.[id]?.name||id)}</h3><p>${relationshipDescription(r)}</p>${(r.impressions||[]).slice(-2).map(x=>`<small class="impression">${escapeHtml(x)}</small>`).join('')}</div></div>`;}).join('')||'<p>You hardly know anyone yet.</p>';}
if(type==='notebook'){const inv=s.investigation||{},ev=(inv.evidence||[]).slice().reverse(),leads=(inv.leads||[]).filter(l=>!l.resolved),connections=inv.connections||[];return `<h3>Unresolved Questions</h3>${leads.map(l=>`<div class="note-card"><strong>${escapeHtml(l.title)}</strong><p>${escapeHtml(l.prompt)}</p></div>`).join('')||'<p>Nothing pressing.</p>'}<h3>Observations</h3>${ev.map(e=>`<div class="note-card"><strong>${escapeHtml(e.title)}</strong><p>${escapeHtml(e.text)}</p></div>`).join('')||'<p>Nothing written down yet.</p>'}<h3>Connections</h3>${connections.map(c=>`<div class="note-card">${escapeHtml(typeof c==='string'?c:JSON.stringify(c))}</div>`).join('')||'<p>No firm connections yet.</p>'}`;}
if(type==='map')return mapHtml(s);if(type==='home')return homeHtml(s);return '';}
const PANEL_TITLES={history:'History',journal:'Journal',map:'Map',inventory:'Inventory',relationships:'Relationships',notebook:'Investigation Notebook',home:'Home'};
function openPanel(type){if(!currentGameData)return;$('panel-title').textContent=PANEL_TITLES[type]||type;const pc=$('panel-content');pc.innerHTML=panelHtml(type);pc.onclick=e=>{const ab=e.target.closest('[data-action-id]');if(ab){closePanel();act(ab.dataset.actionId);return;}const hv=e.target.closest('[data-home-view]');if(hv){const key=hv.dataset.homeView,t=$(`home-${key}-template`),d=$('home-detail');if(t&&d){d.innerHTML=`<h3>${key.charAt(0).toUpperCase()+key.slice(1)}</h3>`+t.innerHTML;}}};$('panel-modal').classList.remove('hidden');}
function closePanel(){$('panel-modal').classList.add('hidden');}function closePanelFromBackdrop(e){if(e.target.id==='panel-modal')closePanel();}
async function act(action){if(requestInFlight)return;requestInFlight=true;const ov=$('loading-overlay'),timer=setTimeout(()=>ov.classList.remove('hidden'),180);document.querySelectorAll('button').forEach(b=>b.disabled=true);try{await fetch('/api/acknowledge',{method:'POST'});const r=await fetch('/api/action',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({action})});render(await r.json());}finally{clearTimeout(timer);ov.classList.add('hidden');document.querySelectorAll('button').forEach(b=>b.disabled=false);requestInFlight=false;}}
function openTalk(a){pendingTalkNpc=a.npc_id;$('talk-title').textContent=`Speak to ${a.npc_name}`;$('talk-input').value='';$('talk-modal').classList.remove('hidden');setTimeout(()=>$('talk-input').focus(),0);}function closeTalk(){$('talk-modal').classList.add('hidden');pendingTalkNpc=null;}
async function sendTalk(){const text=$('talk-input').value.trim();if(!text||!pendingTalkNpc||requestInFlight)return;const npc=pendingTalkNpc;closeTalk();requestInFlight=true;$('loading-overlay').classList.remove('hidden');try{await fetch('/api/acknowledge',{method:'POST'});const r=await fetch('/api/talk',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({npc_id:npc,text})});render(await r.json());}finally{$('loading-overlay').classList.add('hidden');requestInFlight=false;}}
async function lockedUtilityRequest(url){if(requestInFlight)return;requestInFlight=true;$('loading-overlay').classList.remove('hidden');try{const r=await fetch(url,{method:'POST'}),d=await r.json();if(d.message)alert(d.message);render(d.view||d);}catch(e){alert(`Request failed: ${e.message}`);}finally{$('loading-overlay').classList.add('hidden');requestInFlight=false;}}
const saveGame=()=>lockedUtilityRequest('/api/save'),loadGame=()=>lockedUtilityRequest('/api/load');
async function openDeveloperConsole(){if(!devMode())return;developerData=await fetch('/api/developer-status').then(r=>r.json());const d=developerData;$('developer-summary').innerHTML=`<div class="debug-metrics"><div><strong>Version</strong><br>${escapeHtml(d.version)}</div><div><strong>Run</strong><br>${escapeHtml(d.run?.index??1)}</div><div><strong>Day / Time</strong><br>${escapeHtml(d.clock?.day)} · ${escapeHtml(d.clock?.time)}</div><div><strong>Location</strong><br>${escapeHtml(d.player?.location)}</div><div><strong>Pressure</strong><br>${escapeHtml(d.horror?.pressure??0)}</div><div><strong>AI</strong><br>${escapeHtml(d.provider?.state||'unknown')}</div></div>`;const tabs=[['simulation','Simulation'],['npcs','NPCs'],['events','Events'],['horror','Horror'],['investigation','Investigation'],['economy','Economy'],['ai','AI Traces'],['raw','Raw Summary']];$('developer-tabs').innerHTML='';tabs.forEach(([id,label])=>{const b=document.createElement('button');b.textContent=label;b.onclick=()=>renderDeveloperTab(id);$('developer-tabs').appendChild(b);});renderDeveloperTab('simulation');$('developer-modal').classList.remove('hidden');}
function renderDeveloperTab(id){const d=developerData;let value=id==='ai'?{provider:d.provider,runtime:d.ai_runtime,traces:d.traces,events:d.ai_events}:id==='raw'?d:d[id];$('developer-content').innerHTML=`<pre>${escapeHtml(JSON.stringify(value??{},null,2))}</pre>`;}
function closeDeveloperConsole(){$('developer-modal').classList.add('hidden');}function closeDeveloperFromBackdrop(e){if(e.target.id==='developer-modal')closeDeveloperConsole();}
loadAssetManifest().then(()=>{if(currentGameData)applyVisualState(currentGameData);});
document.addEventListener('keydown',e=>{if((e.key==='m'||e.key==='M')&&!['INPUT','TEXTAREA'].includes(document.activeElement?.tagName)){e.preventDefault();openPanel('map');}if(e.key==='Escape'){closePanel();closeTalk();closeDeveloperConsole();}if(e.key==='Enter'&&e.ctrlKey&&!$('talk-modal').classList.contains('hidden'))sendTalk();});fetch('/api/state').then(r=>r.json()).then(render);
