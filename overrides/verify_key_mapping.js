const fs=require('fs'),vm=require('vm');
const src=fs.readFileSync(process.argv[2],'utf8');
function getBlock(startNeedle,endNeedle){
  const a=src.indexOf(startNeedle), b=src.indexOf(endNeedle,a);
  if(a<0||b<0) throw new Error('missing block');
  return src.slice(a,b+endNeedle.length);
}
function assert(c,m){if(!c)throw new Error(m)}
const block=getBlock("const KEYMAP_STORAGE_KEY='cmh.keymap.v1';","document.addEventListener('keydown',handleKeyMappingCapture,true);");
const store=new Map();
const ctx={
  localStorage:{getItem:k=>store.get(k)||null,setItem:(k,v)=>store.set(k,String(v))},
  document:{addEventListener:()=>{}},
  input:{dirs:new Set(),capture:false,dash:false},
  mobileUXActive:()=>false,
  track:()=>{},toast:()=>{},modalLayer:{querySelectorAll:()=>[]},
  openModal:()=>{},$:()=>({}),
};
vm.createContext(ctx);vm.runInContext(block,ctx);
try{
  assert(ctx.keyDisplayName('ArrowUp')==='↑','Arrow display label');
  assert(ctx.keyDisplayName('KeyK')==='K','letter display label');
  assert(vm.runInContext("keyBindingAction('Space')",ctx)==='capture','default capture binding');
  assert(vm.runInContext("keyBindingAction('KeyW')",ctx)==='up','default W binding');
  assert(vm.runInContext("setKeyBinding('capture',0,'KeyF')",ctx)===true,'remap capture to F');
  assert(vm.runInContext("keyBindingAction('KeyF')",ctx)==='capture','new capture binding active');
  assert(vm.runInContext("setKeyBinding('dash',0,'KeyF')",ctx)===false,'duplicate mapping must be rejected');
  assert(store.has('cmh.keymap.v1'),'mapping must persist');
  assert(src.includes('⌨ 키맵핑'),'Korean key mapping label missing');
  assert(src.includes('⚙ 옵션'),'Korean option label missing');
  assert(src.includes("const pressedKeyboardCodes=new Set()"),'mapped input wiring missing');
  assert(src.includes("keyBindingAction(e.code)"),'input must use configurable mapping');
  assert(src.includes("movementKeySummary()+' · 3칸 이상 이동하세요'"),'tutorial must use mapped movement keys');
  console.log('ALL KEY MAPPING TESTS PASS');
}catch(e){console.error('FAIL',e.message);process.exit(1)}
