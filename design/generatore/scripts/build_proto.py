# Rebuilds the "Prototipo guida riprese" flow as one interactive artboard with the guide's design system
# (meadow video, glass, "posa" motion, music and knocks). Run from the guide canvas project folder; writes
# into the prototype canvas folder given as argv[1].
import importlib.util, sys, json

spec = importlib.util.spec_from_file_location("b", "../../scripts/build_screens.py")
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
OUT = sys.argv[1]
DATA = json.load(open("../../scripts/proto_data.json", encoding="utf-8"))

BLOBS = {"42f94be454e116a6ad7236add399e17d": "8ec3f1fa633ba7a58c1af553710c756c",   # meadow photo
         "a78189329319cf3af17d4e9383c05b28": "c08311aba401b5634c4ceb2b469a4baa",   # meadow in the wind
         "01161e9392d0fd17107c9f4de9095ac2": "d6dd3f830358c6b6cb9ee9cf8c8607c8",   # Gymnopédie loop
         "116c5dac2ab57a55619f3f6ee89ec668": "5e6684a3ce03d7a74af4cff8c6b43de9",   # lens map, card
         "a9ba74de8a60ba585f969e9af2a342a4": "af4adb5233848d8abd4191eadd20fbdf",   # lens map, pill
         "7f937f9d5015902de39fec83b78470f3": "6f7dd104080ac8959b6432595e3e268a"}   # lens map, round

EXTRA_CSS = """sc-if,sc-for{display:contents}
/* Glass for a screen that changes all the time: blur and rim over the live background, no measured lens. */
.gl{background:rgba(18,15,9,.18);-webkit-backdrop-filter:blur(16px) saturate(1.45);backdrop-filter:blur(16px) saturate(1.45);border:1px solid rgba(255,255,255,.18);box-shadow:inset 1.5px 1.5px 0 rgba(255,255,255,.45),inset -1px -1px 0 rgba(255,255,255,.14),inset 0 0 24px rgba(255,255,255,.08),0 14px 34px -16px rgba(8,6,3,.6);text-shadow:0 1px 10px rgba(10,8,4,.4);color:#F3EBDD;box-sizing:border-box}
button.gl{cursor:pointer;transition:transform .25s cubic-bezier(.3,.7,.2,1),background .25s}
button.gl:active{transform:scale(.965)}
button.gl:hover{background:rgba(255,255,255,.08)}
button.btn-p{border:0;cursor:pointer}
.icon-btn{width:44px;height:44px;border-radius:50%;display:grid;place-items:center}
.li-row{display:grid;grid-template-columns:34px 1fr;gap:6px;padding:11px 0;font-size:15px;line-height:1.45}
.li-row+.li-row{border-top:1px solid rgba(243,235,221,.14)}
.irow{display:grid;grid-template-columns:34px 1fr;gap:10px;padding:13px 0}.irow+.irow{border-top:1px solid rgba(243,235,221,.14)}
.irow-i{color:#E6D3B0;padding-top:1px}.irow-t{font-size:15px;font-weight:600}.irow-p{font-size:13px;line-height:1.5;color:rgba(243,235,221,.85)}
.tile{display:grid;grid-template-columns:72px 1fr;align-items:center;gap:14px;width:100%;min-height:92px;padding:12px 18px;border-radius:22px;text-align:left}
.ptile{display:flex;flex-direction:column;gap:8px;padding:10px 10px 12px;border-radius:20px;width:100%}
.plan{position:relative}
.pnum{position:absolute;transform:translate(-50%,-50%);font:700 9px Archivo,system-ui,sans-serif;color:#F3EBDD;pointer-events:none}
.plbl{position:absolute;transform:translate(-50%,-50%);font-family:Archivo,system-ui,sans-serif;font-stretch:125%;font-size:8px;letter-spacing:.2em;text-transform:uppercase;color:rgba(243,235,221,.85);pointer-events:none}
.pdot{position:absolute;width:18px;height:18px;margin:-9px 0 0 -9px;box-sizing:border-box;border-radius:50%;display:grid;place-items:center;font:700 9px Archivo,system-ui,sans-serif;pointer-events:none}
/* Points: dark still to reach, white the one of this step (with a ring), champagne already done. */
.pdot.todo{background:#2a2f1c;border:1px solid rgba(243,235,221,.7);color:#F3EBDD;font-weight:500}
.pdot.cur{background:#F3EBDD;color:#17130C}
.pdot.done{background:#D9C29A;color:#17130C}
.pdot.cur::after{content:"";position:absolute;inset:-3px;border-radius:50%;border:1.2px solid #D9C29A;animation:ring 1.8s ease-out infinite}
@keyframes ring{from{transform:scale(.85);opacity:.9}to{transform:scale(2);opacity:0}}
.f-fig{filter:url(#lgFig)}.f-back{filter:url(#lgBack)}
/* Arrows: dashed, drawn one dash after the other right after the point to record from appears, then still. */
.dsh{fill:#D9C29A;stroke:#D9C29A;stroke-width:4.5;stroke-linecap:round;stroke-linejoin:round}
.anim .dsh{animation:fade 160ms ease-out calc(var(--show,0ms) + var(--k) * var(--dstep,50ms)) backwards}
/* The cone (and the person, when walking) arrives with the point. */
.anim .appear{animation:fade 420ms cubic-bezier(.22,1,.36,1) var(--show,0ms) backwards}
@media (prefers-reduced-motion: reduce){.anim .dsh,.anim .appear{animation:none}}
/* Turning: the camera cone sweeps along the arc, rests, and starts again. */
/* Both wait until every point of the plan has appeared (--wait), and restart with the screen. */
.cone-rot{transform-box:view-box;transform-origin:0 0;transform:rotate(var(--from))}
.anim .cone-rot{animation:cone-sweep var(--rdur,6s) linear var(--wait,0ms) infinite backwards}
/* Real pace: the move takes 84% of the cycle (6% still at the start, 10% at the end), at a steady speed. */
@keyframes cone-sweep{0%,6%{transform:rotate(var(--from))}90%,100%{transform:rotate(var(--to))}}
/* Walking: the person and the cone travel along the route, facing the way they go. */
.walker{transform-box:view-box;transform-origin:0 0;offset-rotate:auto;offset-distance:0%}
.anim .walker{animation:walk var(--wdur,4s) linear var(--wait,0ms) infinite backwards}
@keyframes walk{0%,6%{offset-distance:0%}90%,100%{offset-distance:100%}}
@media (prefers-reduced-motion: reduce){.anim .cone-rot,.anim .walker{animation:none}}
.mini .pdot,.mini .plbl{display:none}
.mini .pdot.cur{display:grid;width:15px;height:15px;margin:-7.5px 0 0 -7.5px;font-size:8px}
.ph{margin-top:12px;min-height:84px;border-radius:18px;border-style:dashed;display:grid;place-items:center;align-content:center;gap:4px;text-align:center;padding:10px}
.stop{position:absolute;left:50%;margin-left:-42px;bottom:40px;width:84px;height:84px;border-radius:50%;border:2px solid #F3EBDD;background:transparent;display:grid;place-items:center;cursor:pointer;transition:transform .25s cubic-bezier(.3,.7,.2,1)}
.stop:active{transform:scale(.94)}
/* Follow the arrow, set in the room: 6 px of screen for each degree turned (about what the 0.5× lens shows across the
   screen). Line and arrow live in a layer that slides by the degrees turned; the arrow slides on it by the degrees it
   should be at. Both only move (transform), so the phone draws them without redrawing the page. */
.aim{position:absolute;left:50%;top:50%;width:0;height:0;pointer-events:none}
.aim-world{position:absolute;left:0;top:0;will-change:transform}
.aim-line{position:absolute;left:0;top:-1.5px;width:var(--len);height:3px;background:repeating-linear-gradient(90deg,#F3EBDD 0 11px,transparent 11px 23px);filter:drop-shadow(0 0 2px rgba(10,8,4,.7))}
.aim-end{position:absolute;left:var(--len);top:-10px;width:20px;height:20px;margin-left:-10px;border-radius:50%;border:2.5px solid #D9C29A;box-sizing:border-box;filter:drop-shadow(0 0 2px rgba(10,8,4,.6))}
.aim-arrow{position:absolute;left:-15px;top:-15px;width:30px;height:30px;border-radius:50%;background:#D9C29A;display:grid;place-items:center;box-shadow:0 0 0 4px rgba(217,194,154,.25),0 4px 14px -4px rgba(8,6,3,.7);will-change:transform}
.aim-you{position:absolute;left:-24px;top:-24px;width:48px;height:48px;border-radius:50%;border:2.5px solid #F3EBDD;box-sizing:border-box;box-shadow:0 0 0 1px rgba(10,8,4,.35),inset 0 0 0 1px rgba(10,8,4,.35)}
.anim .aim-world{animation:aim-world var(--rdur,6s) linear both}
.anim .aim-arrow{animation:aim-arrow var(--rdur,6s) linear both}
@keyframes aim-world{0%,6%{transform:translateX(0)}90%,100%{transform:translateX(calc(var(--len) * -1))}}
@keyframes aim-arrow{0%,6%{transform:translateX(0)}90%,100%{transform:translateX(var(--len))}}
@media (prefers-reduced-motion: reduce){.anim .aim-world,.anim .aim-arrow{animation:none}}
/* Ready to record: the camera's own red button, with the plan on one side and skipping on the other. */
.recb{position:absolute;left:50%;margin-left:-42px;bottom:40px;width:84px;height:84px;border-radius:50%;border:3px solid #F3EBDD;background:transparent;display:grid;place-items:center;cursor:pointer;padding:0;transition:transform .25s cubic-bezier(.3,.7,.2,1)}
.recb span{width:66px;height:66px;border-radius:50%;background:#E0583F}
.recb:active{transform:scale(.94)}
.rec-pill{display:inline-flex;align-items:center;gap:8px;height:48px;padding:0 18px;border-radius:999px;font:600 14px Archivo,system-ui,sans-serif;white-space:nowrap}
.rec-side{position:absolute;bottom:58px}
.chip.chip-note{position:static;opacity:1;background:rgba(18,15,9,.62);color:#F3EBDD;-webkit-backdrop-filter:blur(14px);backdrop-filter:blur(14px);border:1px solid rgba(255,255,255,.18);white-space:normal;text-align:center;height:auto;min-height:40px;padding:8px 16px}
/* Same lift as "posa" for glass, which can't sit in a clipping wrapper: it fades in instead of rising from a line. */
.free{transform-origin:20% 100%;--tilt:-.9deg;--dur:820ms}
.anim .free{animation:posa-free var(--dur) linear var(--d,0ms) backwards}
@keyframes posa-free{0%{opacity:0;transform:translateY(40px) rotate(calc(var(--tilt) * 1.4));animation-timing-function:cubic-bezier(.2,.75,.25,1)}25%{opacity:1}58%{transform:translateY(-9px) rotate(var(--tilt));animation-timing-function:cubic-bezier(.45,0,.3,1)}100%{opacity:1;transform:translateY(0) rotate(0deg)}}
/* Between screens the motion is reset for a frame, so the next screen's pieces set down again. */
.prep .scr{opacity:0}
@keyframes blink{50%{opacity:.25}}
.rec-dot{animation:blink 1.4s steps(1) infinite}
/* Pencil boil: three takes of each sketch, one visible at a time, about eight changes a second. */
.boil{opacity:0;animation:boil .42s steps(1) infinite}.boil.b2{animation-delay:-.14s}.boil.b3{animation-delay:-.28s}
@keyframes boil{0%{opacity:1}33.333%{opacity:0}100%{opacity:0}}
/* ---- First-person view: what the phone sees in this step, sketched from the plan ---- */
.views{display:grid}.views>*{grid-area:1/1;transition:opacity .35s ease}
.views.v-plan .fp-view,.views.v-fp .plan{opacity:0;visibility:hidden}
.fp-view{border-radius:14px;overflow:hidden;background:rgba(18,15,9,.12)}
.seg-btn[aria-pressed="true"]{background:#D9C29A;color:#17130C;box-shadow:none}
.fp-move{transform-box:view-box;transform-origin:50% 50%}
/* Turning: the room slides by as the phone turns, in step with the cone on the plan. */
.anim .fp-move.fp-turn{animation:fp-pan var(--rdur,6s) linear var(--wait,0ms) infinite backwards}
@keyframes fp-pan{0%,6%{transform:translateX(0)}90%,100%{transform:translateX(var(--sx))}}
/* Walking: the view comes closer, in step with the person on the plan. */
.anim .fp-move.fp-walk{animation:fp-zoom var(--wdur,6s) linear var(--wait,0ms) infinite backwards}
@keyframes fp-zoom{0%,6%{transform:scale(1)}90%,100%{transform:scale(var(--zoom))}}
@media (prefers-reduced-motion: reduce){.anim .fp-move{animation:none}}
/* Skipping a point: a quiet dashed line under the plan, never competing with Registra. */
.skip-btn{display:flex;align-items:center;justify-content:center;gap:14px;width:100%;min-height:72px;padding:12px 20px;box-sizing:border-box;border-radius:22px;background:rgba(18,15,9,.32);-webkit-backdrop-filter:blur(14px);backdrop-filter:blur(14px);border:1.5px dashed rgba(217,194,154,.7);color:#F3EBDD;font:600 16px/1.35 Archivo,system-ui,sans-serif;text-align:left;text-shadow:0 1px 10px rgba(10,8,4,.45);cursor:pointer;transition:transform .25s cubic-bezier(.3,.7,.2,1)}
.skip-btn:active{transform:scale(.98)}.skip-btn svg{flex:none}
/* The brand, small at the very top, in the guide's Vogue-like display face: wide letters, pressed flat. */
.brand{position:absolute;top:21px;left:0;right:0;margin:0;text-align:center;font:500 11px/1 var(--display);letter-spacing:.62em;text-indent:.62em;color:rgba(243,235,221,.86);transform:scaleY(.78);text-shadow:0 1px 8px rgba(10,8,4,.45);pointer-events:none}
/* ---- Feedback ---- */
.fb-pill{display:inline-flex;align-items:center;gap:7px;height:44px;padding:0 15px;border-radius:999px;font-family:Archivo,system-ui,sans-serif;font-size:13px;font-weight:600;letter-spacing:.01em;white-space:nowrap}
.fb-sheet{animation:posa-free 700ms linear backwards;--tilt:0deg}
.star{width:44px;height:44px;display:grid;place-items:center;border:0;background:none;padding:0;cursor:pointer;transition:transform .2s cubic-bezier(.3,.7,.2,1)}
.star:active{transform:scale(.9)}
.star:focus-visible,.fb-text:focus-visible{outline:2px solid #D9C29A;outline-offset:2px}
.fb-text{width:100%;border-radius:18px;padding:14px 16px;font:400 16px/1.4 Archivo,system-ui,sans-serif;color:#F3EBDD;resize:none}
.fb-text::placeholder{color:rgba(243,235,221,.6)}
@media (prefers-reduced-motion: reduce){.fb-sheet{animation:fade .3s ease backwards}}
/* ---- Recording guidance ---- */
.dial-prog{stroke-dasharray:553;stroke-dashoffset:553;animation:dial var(--rdur,6s) linear infinite}
@keyframes dial{0%,6%{stroke-dashoffset:553}90%,100%{stroke-dashoffset:var(--end)}}
.dial-mark{transform-box:view-box;transform-origin:0 0;animation:dial-mark var(--rdur,6s) linear infinite}
@keyframes dial-mark{0%,6%{transform:rotate(0deg)}90%,100%{transform:rotate(var(--deg))}}
.chev{opacity:.25;animation:chev 1.2s ease-in-out infinite}.chev.c2{animation-delay:.2s}.chev.c3{animation-delay:.4s}
@keyframes chev{0%,100%{opacity:.25}40%{opacity:1}}
.walk-bar{transform-origin:left center;animation:walkbar var(--wdur,4s) linear infinite}
@keyframes walkbar{0%,6%{transform:scaleX(0)}90%,100%{transform:scaleX(1)}}
.level{transform-origin:50% 50%;transition:transform .5s cubic-bezier(.3,.7,.2,1)}
.lv{background:#D9C29A;transition:background .4s}
/* One warning at a time. Green-free palette: calm glass when all is well, rec red to slow down, champagne to level. */
.chip{position:absolute;display:inline-flex;align-items:center;gap:8px;height:40px;padding:0 16px;border-radius:999px;font-size:14px;font-weight:600;opacity:0;white-space:nowrap}
.chip-piano{background:rgba(224,88,63,.92);color:#F3EBDD;box-shadow:0 10px 26px -12px rgba(0,0,0,.6)}
.chip-dritto{background:#D9C29A;color:#17130C;box-shadow:0 10px 26px -12px rgba(0,0,0,.6)}
.chip-luce{color:#E6D3B0}
.avv-auto .chip{animation:chip 15s infinite}
.avv-auto .chip-piano{animation-delay:5s}.avv-auto .chip-dritto{animation-delay:10s}.avv-auto .chip-luce{animation:none}
@keyframes chip{0%{opacity:0}2%,30%{opacity:1}33.3%,100%{opacity:0}}
.avv-auto .level{animation:tilt 15s infinite}.avv-auto .lv{animation:lv 15s infinite}
@keyframes tilt{0%,67%{transform:rotate(0deg)}70%,96%{transform:rotate(7deg)}99%,100%{transform:rotate(0deg)}}
@keyframes lv{0%,67%{background:#D9C29A}70%,96%{background:#E0583F}99%,100%{background:#D9C29A}}
.avv-piano .chip-piano,.avv-dritto .chip-dritto,.avv-luce .chip-luce,.avv-ok .chip-ok{opacity:1}
.avv-dritto .level{transform:rotate(7deg)}.avv-dritto .lv{background:#E0583F}
@media (prefers-reduced-motion: reduce){.dial-prog,.dial-mark,.chev,.walk-bar,.avv-auto .chip,.avv-auto .level,.avv-auto .lv{animation:none}.chev{opacity:1}}
@media (prefers-reduced-motion: reduce){.anim .free{animation:fade .4s ease var(--d,0ms) backwards}.rec-dot{animation:none}.boil{animation:none}.boil.b1{opacity:1}}
/* The shadow behind the words on the meadow: a tight dark edge for the letters and a wide soft halo for the line, like light on velvet (same as the questionnaire). */
.prato .scr :is(h1,h2,p,.lab,.dsp),.prato .brand{text-shadow:0 1px 2px rgba(10,8,4,.5),0 2px 14px rgba(10,8,4,.6),0 0 34px rgba(10,8,4,.45)}
.prato .scr.scr h1{text-shadow:0 1px 3px rgba(10,8,4,.45),0 4px 26px rgba(10,8,4,.6),0 0 64px rgba(10,8,4,.45)}
.prato .scr :is(.lg-c,.gl,.btn-p) :is(h1,h2,p,.lab,.dsp){text-shadow:0 1px 10px rgba(10,8,4,.4)}"""

def plan_html(p):
    return """<div class="plan">
            <svg viewBox="0 0 1000 700" width="100%" role="img" aria-label="{{ P.label }}" style="display: block; --show: {{ P.show }}">
              <path d="{{ P.bgd }}" fill="rgba(18,15,9,.24)"></path>
              <path d="{{ P.fill }}" fill="rgba(18,15,9,.22)"></path>
              <path d="{{ P.stairs }}" fill="none" stroke="rgba(243,235,221,.3)" stroke-width="3"></path>
              <path d="{{ P.walls }}" fill="none" stroke="rgba(243,235,221,.75)" stroke-width="4" stroke-linejoin="round"></path>
              <path d="{{ P.inner }}" fill="none" stroke="rgba(243,235,221,.75)" stroke-width="4"></path>
              <path d="{{ P.newel }}" fill="rgba(243,235,221,.75)"></path>
              <path d="{{ P.door }}" fill="none" stroke="#3c4526" stroke-width="16"></path>
              <path d="{{ P.icon }}" fill="#D9C29A"></path>
              <path d="{{ P.cone }}" fill="rgba(217,194,154,.22)"></path>
              <g style="--dstep: {{ P.dstep }}">
              <path class="dsh" d="{{ P.dz.d0 }}" style="--k: 0"></path>
              <path class="dsh" d="{{ P.dz.d1 }}" style="--k: 1"></path>
              <path class="dsh" d="{{ P.dz.d2 }}" style="--k: 2"></path>
              <path class="dsh" d="{{ P.dz.d3 }}" style="--k: 3"></path>
              <path class="dsh" d="{{ P.dz.d4 }}" style="--k: 4"></path>
              <path class="dsh" d="{{ P.dz.d5 }}" style="--k: 5"></path>
              <path class="dsh" d="{{ P.dz.d6 }}" style="--k: 6"></path>
              <path class="dsh" d="{{ P.dz.d7 }}" style="--k: 7"></path>
              <path class="dsh" d="{{ P.dz.d8 }}" style="--k: 8"></path>
              <path class="dsh" d="{{ P.dz.d9 }}" style="--k: 9"></path>
              <path class="dsh" d="{{ P.dz.d10 }}" style="--k: 10"></path>
              <path class="dsh" d="{{ P.dz.d11 }}" style="--k: 11"></path>
              <path class="dsh" d="{{ P.dz.d12 }}" style="--k: 12"></path>
              <path class="dsh" d="{{ P.dz.d13 }}" style="--k: 13"></path>
              <path class="dsh" d="{{ P.dz.d14 }}" style="--k: 14"></path>
              <path class="dsh" d="{{ P.dz.d15 }}" style="--k: 15"></path>
              <path class="dsh" d="{{ P.dz.d16 }}" style="--k: 16"></path>
              <path class="dsh" d="{{ P.dz.d17 }}" style="--k: 17"></path>
              <path class="dsh" d="{{ P.dz.d18 }}" style="--k: 18"></path>
              <path class="dsh" d="{{ P.dz.d19 }}" style="--k: 19"></path>
              <path class="dsh" d="{{ P.dz.d20 }}" style="--k: 20"></path>
              <path class="dsh" d="{{ P.dz.d21 }}" style="--k: 21"></path>
              <path class="dsh" d="{{ P.dz.d22 }}" style="--k: 22"></path>
              <path class="dsh" d="{{ P.dz.d23 }}" style="--k: 23"></path>
              <path class="dsh" d="{{ P.dz.d24 }}" style="--k: 24"></path>
              <path class="dsh" d="{{ P.dz.d25 }}" style="--k: 25"></path>
              <path class="dsh" d="{{ P.dz.d26 }}" style="--k: 26"></path>
              <path class="dsh" d="{{ P.dz.d27 }}" style="--k: 27"></path>
              <path class="dsh" d="{{ P.dz.d28 }}" style="--k: 28"></path>
              <path class="dsh" d="{{ P.dz.d29 }}" style="--k: 29"></path>
              <path class="dsh" d="{{ P.dz.d30 }}" style="--k: 30"></path>
              <path class="dsh" d="{{ P.dz.d31 }}" style="--k: 31"></path>
              <path class="dsh" d="{{ P.dz.d32 }}" style="--k: 32"></path>
              <path class="dsh" d="{{ P.dz.d33 }}" style="--k: 33"></path>
              <path class="dsh" d="{{ P.dz.d34 }}" style="--k: 34"></path>
              <path class="dsh" d="{{ P.dz.d35 }}" style="--k: 35"></path>
              <path class="dsh" d="{{ P.dz.d36 }}" style="--k: 36"></path>
              <path class="dsh" d="{{ P.dz.d37 }}" style="--k: 37"></path>
              <path class="dsh" d="{{ P.dz.d38 }}" style="--k: 38"></path>
              <path class="dsh" d="{{ P.dz.d39 }}" style="--k: 39"></path>
              <path class="dsh" d="{{ P.dz.d40 }}" style="--k: 40"></path>
              <path class="dsh" d="{{ P.dz.d41 }}" style="--k: 41"></path>
              <path class="dsh" d="{{ P.dz.d42 }}" style="--k: 42"></path>
              <path class="dsh" d="{{ P.dz.d43 }}" style="--k: 43"></path>
              <path class="dsh" d="{{ P.dz.d44 }}" style="--k: 44"></path>
              <path class="dsh" d="{{ P.dz.d45 }}" style="--k: 45"></path>
              <path class="dsh" d="{{ P.dz.d46 }}" style="--k: 46"></path>
              <path class="dsh" d="{{ P.dz.d47 }}" style="--k: 47"></path>
              <path class="dsh" d="{{ P.dz.d48 }}" style="--k: 48"></path>
              <path class="dsh" d="{{ P.dz.d49 }}" style="--k: 49"></path>
              <path class="dsh" d="{{ P.dz.d50 }}" style="--k: 50"></path>
              <path class="dsh" d="{{ P.dz.d51 }}" style="--k: 51"></path>
              <path class="dsh" d="{{ P.dz.d52 }}" style="--k: 52"></path>
              <path class="dsh" d="{{ P.dz.d53 }}" style="--k: 53"></path>
              <path class="dsh" d="{{ P.dz.d54 }}" style="--k: 54"></path>
              <path class="dsh" d="{{ P.dz.d55 }}" style="--k: 55"></path>
              <path class="dsh" d="{{ P.dz.d56 }}" style="--k: 56"></path>
              <path class="dsh" d="{{ P.dz.d57 }}" style="--k: 57"></path>
              <path class="dsh" d="{{ P.dz.d58 }}" style="--k: 58"></path>
              <path class="dsh" d="{{ P.dz.d59 }}" style="--k: 59"></path>
              <path class="dsh" d="{{ P.dz.d60 }}" style="--k: 60"></path>
              <path class="dsh" d="{{ P.dz.d61 }}" style="--k: 61"></path>
              <path class="dsh" d="{{ P.dz.d62 }}" style="--k: 62"></path>
              <path class="dsh" d="{{ P.dz.d63 }}" style="--k: 63"></path>
              <path class="dsh" d="{{ P.dz.d64 }}" style="--k: 64"></path>
              <path class="dsh" d="{{ P.dz.d65 }}" style="--k: 65"></path>
              <path class="dsh" d="{{ P.dz.d66 }}" style="--k: 66"></path>
              <path class="dsh" d="{{ P.dz.d67 }}" style="--k: 67"></path>
              <path class="dsh" d="{{ P.dz.d68 }}" style="--k: 68"></path>
              <path class="dsh" d="{{ P.dz.d69 }}" style="--k: 69"></path>
              <path class="dsh" d="{{ P.dz.d70 }}" style="--k: 70"></path>
              <path class="dsh" d="{{ P.dz.d71 }}" style="--k: 71"></path>
              </g>
              <path d="{{ P.person }}" fill="#F3EBDD"></path>
              <path d="{{ P.tick }}" fill="none" stroke="#17130C" stroke-width="6" stroke-linecap="round"></path>
              <g class="appear" transform="translate({{ P.tx }} {{ P.ty }})" style="display: {{ P.turnDisp }}">
                <g class="cone-rot" style="--from: {{ P.rf }}; --to: {{ P.rt }}; --wait: {{ P.wait }}; --rdur: {{ P.rdur }}"><path d="M0,0 L117,-65 A134,134 0 0,1 117,65 Z" fill="rgba(217,194,154,.3)" stroke="#D9C29A" stroke-width="2"></path></g>
              </g>
              <g class="appear" style="display: {{ P.walkDisp }}"><g class="walker" style="offset-path: path('{{ P.route }}'); --wdur: {{ P.wdur }}; --wait: {{ P.wait }}">
                <path d="M0,0 L130,-75 A150,150 0 0,1 130,75 Z" fill="rgba(217,194,154,.3)" stroke="#D9C29A" stroke-width="2"></path>
                <circle r="20" fill="#F3EBDD"></circle>
                <path d="M0,0 L26,0" stroke="#17130C" stroke-width="6" stroke-linecap="round"></path>
              </g></g>
            </svg>
            <sc-for list="{{ P.nums }}" as="n" hint-placeholder-count="0"><span class="pdot pt {{n.st}}" style="left: {{n.x}}; top: {{n.y}}; --i: {{n.i}}">{{n.n}}</span></sc-for>
            <sc-for list="{{ P.labels }}" as="l" hint-placeholder-count="0"><span class="plbl" style="left: {{l.x}}; top: {{l.y}}">{{l.t}}</span></sc-for>
          </div>""".replace("P.", p + ".")

ICON = lambda d, w=20: f'<svg width="{w}" height="{w}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{d}</svg>'
CHEV_L = ICON('<path d="M14.5 5.5L8 12l6.5 6.5"></path>')
CHEV_R = ICON('<path d="M9.5 5.5L16 12l-6.5 6.5"></path>')
CLOSE = ICON('<path d="M6 6l12 12M18 6L6 18"></path>')
REDO = ICON('<path d="M4.5 12a7.5 7.5 0 1 0 2.2-5.3"></path><path d="M4.5 4.5v4h4"></path>', 18)
SHAPE_I = ICON('<path d="M4 6h9v12H4z"></path><path d="M16 7l4 5-4 5"></path>', 18)
PLAN_I = ICON('<path d="M4 5h16v14H4z"></path><path d="M11 5v6H4M15 19v-5h5"></path>', 18)
SKIP_I = ICON('<path d="M5 5.5l7 6.5-7 6.5M12.5 5.5l7 6.5-7 6.5"></path>', 18)
SPK_ON = ICON('<path d="M4 9.5h3.5L12 5.5v13l-4.5-4H4z"></path><path d="M15.5 9a4 4 0 0 1 0 6M18 6.5a7.5 7.5 0 0 1 0 11"></path>', 18)
SPK_OFF = ICON('<path d="M4 9.5h3.5L12 5.5v13l-4.5-4H4z"></path><path d="M16 9.5l5 5M21 9.5l-5 5"></path>', 18)
EYE = ICON('<path d="M2.5 12s3.5-6 9.5-6 9.5 6 9.5 6-3.5 6-9.5 6-9.5-6-9.5-6z"></path><circle cx="12" cy="12" r="2.8"></circle>', 18)
SPACE_ICONS = {
    "ambiente": '<path d="M30,35 L60,20 L95,30 L95,65 L60,78 L30,66 Z M30,35 L65,45 L95,30 M65,45 L60,78"></path>',
    "corridoio": '<path d="M25,12 H95 V80 H25 Z M45,30 H75 V62 H45 Z M25,12 L45,30 M95,12 L75,30 M25,80 L45,62 M95,80 L75,62"></path>',
    "scala": '<path d="M20,78 H40 V62 H58 V46 H76 V30 H94 V14"></path>',
}
# Sketched icons: pencil lines that "boil". Each icon is drawn in three takes, each through its own wobble
# filter (different noise seed), and the takes swap a few times a second, so the strokes keep moving.
def _ext(x1, y1, x2, y2, o=2.2):
    import math
    L = math.hypot(x2 - x1, y2 - y1) or 1
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    return f"M{x1 - ux * o:.1f} {y1 - uy * o:.1f} L{x2 + ux * o:.1f} {y2 + uy * o:.1f} "
def _segs(points):
    return [(points[i], points[i + 1]) for i in range(len(points) - 1)]
CUBE_FRONT = [(30, 36), (70, 36), (70, 76), (30, 76), (30, 36)]
SKETCH = {
    # Cabinet cube: front face, top and right faces visible, the three back edges dashed.
    "ambiente": {"lines": _segs(CUBE_FRONT) + [((30, 36), (50, 20)), ((70, 36), (90, 20)), ((50, 20), (90, 20)), ((70, 76), (90, 60)), ((90, 20), (90, 60))],
                 "hidden": [((50, 20), (50, 60)), ((50, 60), (90, 60)), ((30, 76), (50, 60))]},
    # Corridor in one-point perspective: the frame, a narrow tall far end, and the four edges running to it.
    "corridoio": {"lines": _segs([(22, 10), (98, 10), (98, 80), (22, 80), (22, 10)]) + _segs([(52, 30), (68, 30), (68, 62), (52, 62), (52, 30)])
                  + [((22, 10), (52, 30)), ((98, 10), (68, 30)), ((98, 80), (68, 62)), ((22, 80), (52, 62))], "hidden": []},
    "scala": {"lines": _segs([(20, 78), (40, 78), (40, 62), (58, 62), (58, 46), (76, 46), (76, 30), (94, 30), (94, 14)]), "hidden": []},
}
# Hatching that shades a face, like a quick pencil study: a few light strokes, never filling the shape.
HATCH = {
    "ambiente": [((71 + k * 2.6, 75 - k * 2.1), (75 + k * 2.6, 40 - k * 3.1)) for k in range(7)],
    "corridoio": [((24 + k * 4.2, 74 - k * 2.5), (24 + k * 4.2 + 3, 18 + k * 1.6)) for k in range(6)],
    # a few short strokes on each riser, just under the tread
    "scala": [((x - 3 - k * 3.2, y + 14), (x - 1 - k * 3.2, y + 4)) for x, y in ((40, 62), (58, 46), (76, 30), (94, 14)) for k in range(3)],
}
def _stroke(rng, p1, p2, w, op, over=(0.6, 3.2), S=1):
    import math
    (x1, y1), (x2, y2) = p1, p2
    L = math.hypot(x2 - x1, y2 - y1) or 1
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    j = lambda: rng.uniform(-0.9, 0.9) * S
    o1, o2 = rng.uniform(*over) * S, rng.uniform(*over) * S
    ax, ay = x1 - ux * o1 + j(), y1 - uy * o1 + j()
    bx, by = x2 + ux * o2 + j(), y2 + uy * o2 + j()
    bend = rng.uniform(-1.4, 1.4) * S
    cx, cy = (ax + bx) / 2 - uy * bend, (ay + by) / 2 + ux * bend
    return f'<path d="M{ax:.1f} {ay:.1f} Q{cx:.1f} {cy:.1f} {bx:.1f} {by:.1f}" stroke-width="{w * S:.2f}" opacity="{op:.2f}"></path>'

# One freehand pass along a chain of points, drawn the way the oval and the circle are: a single continuous line
# with a slow wobble, the whole pass a little shifted, scaled and turned, and closed shapes running past the start.
def _chain_pass(rng, pts, closed, S, w, op, dash="", jit=1.0):
    import math
    pts = list(pts) + ([pts[0]] if closed else [])
    cx = sum(x for x, _ in pts) / len(pts); cy = sum(y for _, y in pts) / len(pts)
    # jit < 1 keeps the passes (and the takes) closer together, so the drawing shakes less from take to take
    sc = 1 + rng.uniform(-0.02, 0.02) * jit; rot = math.radians(rng.uniform(-2, 2) * jit); dx, dy = rng.uniform(-0.8, 0.8) * S * jit, rng.uniform(-0.8, 0.8) * S * jit
    segs = [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    lens = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in segs]
    P = sum(lens)
    def at(u):  # point and unit normal at arc length u along the chain (wrapping for closed shapes)
        u = u % P if closed else max(0, min(P, u))
        for (a, b), L in zip(segs, lens):
            if u <= L or (a, b) == segs[-1]:
                t = min(1, u / L) if L else 0
                ux, uy = ((b[0] - a[0]) / L, (b[1] - a[1]) / L) if L else (1, 0)
                return a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, -uy, ux
            u -= L
    amp = min(1, P / (120 * S))  # short lines wobble less, or they turn into waves
    k1, k2, ph1, ph2 = rng.uniform(1.0, 1.8) * S * amp, rng.uniform(0.2, 0.45) * S * amp, rng.uniform(0, 6.28), rng.uniform(0, 6.28)
    if closed:
        start, length = rng.uniform(0, P), P * (1 + rng.uniform(0.03, 0.08))
    else:
        o1, o2 = rng.uniform(0.5, 2.5) * S, rng.uniform(0.5, 2.5) * S
        start, length = -o1, P + o1 + o2
    n = max(12, int(length / (2 * S)))
    out = []
    for i in range(n + 1):
        u = start + length * i / n
        if not closed and (u < 0 or u > P):  # running past the ends of an open line
            (x, y, nx, ny) = at(0 if u < 0 else P)
            a, b = (segs[0] if u < 0 else segs[-1])
            L = math.hypot(b[0] - a[0], b[1] - a[1]) or 1
            ex = u if u < 0 else u - P
            x += (b[0] - a[0]) / L * ex; y += (b[1] - a[1]) / L * ex
        else:
            x, y, nx, ny = at(u)
        wob = k1 * math.sin(2 * math.pi * 2 * u / P + ph1) + k2 * math.sin(2 * math.pi * 5 * u / P + ph2)
        x, y = x + nx * wob * 0.6, y + ny * wob * 0.6
        x, y = cx + (x - cx) * sc, cy + (y - cy) * sc
        x, y = cx + (x - cx) * math.cos(rot) - (y - cy) * math.sin(rot) + dx, cy + (x - cx) * math.sin(rot) + (y - cy) * math.cos(rot) + dy
        out.append(f"{x:.1f} {y:.1f}")
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="M{" L".join(out)}" stroke-width="{w * S:.2f}" opacity="{op:.2f}"{da}></path>'
def _passes(rng, pts, closed, S, dash="", jit=1.0):
    out = []
    for k in range(rng.choice((2, 3, 3)) if not dash else 2):
        w = rng.uniform(0.8, 1.5) if k == 0 else rng.uniform(0.5, 0.9)
        op = rng.uniform(0.75, 0.95) if k == 0 else rng.uniform(0.35, 0.6)
        if dash:
            w, op = 0.8, (0.6 if k == 0 else 0.35)
        out.append(_chain_pass(rng, pts, closed, S, w, op, dash, jit))
    return out
# The three space icons as chains: (points, closed, dashed).
CHAINS = {
    "ambiente": [([(30, 36), (70, 36), (70, 76), (30, 76)], True, ""), ([(30, 36), (50, 20), (90, 20), (70, 36)], True, ""),
                 ([(70, 36), (90, 20), (90, 60), (70, 76)], True, ""),
                 ([(50, 20), (50, 60), (90, 60)], False, "3 3.4"), ([(30, 76), (50, 60)], False, "3 3.4")],
    "corridoio": [([(22, 10), (98, 10), (98, 80), (22, 80)], True, ""), ([(52, 30), (68, 30), (68, 62), (52, 62)], True, ""),
                  ([(22, 10), (52, 30)], False, ""), ([(98, 10), (68, 30)], False, ""), ([(98, 80), (68, 62)], False, ""), ([(22, 80), (52, 62)], False, "")],
    "scala": [([(20, 78), (40, 78), (40, 62), (58, 62), (58, 46), (76, 46), (76, 30), (94, 30), (94, 14)], False, "")],
}
def sketch_icon(key):
    import random
    takes = []
    for n in (1, 2, 3):
        rng = random.Random(f"{key}-{n}")
        parts = []
        for pts, closed, dash in CHAINS[key]:
            parts += _passes(rng, pts, closed, 1, dash)
        takes.append(f'<g class="boil b{n}" filter="url(#sk{n})" stroke="#EFE8DC">' + "".join(parts) + "</g>")
    return ('<svg viewBox="0 0 120 90" width="72" height="54" fill="none" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
            + "".join(takes) + "</svg>")
SKETCH_FILTERS = '<svg width="0" height="0" style="position: absolute" aria-hidden="true"><defs>' + "".join(
    f'<filter id="sk{n}" x="-15%" y="-15%" width="130%" height="130%">'
    f'<feTurbulence type="fractalNoise" baseFrequency="0.05" numOctaves="2" seed="{n * 7}" result="w"></feTurbulence>'
    f'<feDisplacementMap in="SourceGraphic" in2="w" scale="1.6" xChannelSelector="R" yChannelSelector="G" result="d"></feDisplacementMap>'
    f'<feTurbulence type="fractalNoise" baseFrequency="1.1" numOctaves="1" seed="{n * 13}" result="g"></feTurbulence>'
    f'<feColorMatrix in="g" type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 -0.9 1.45" result="ga"></feColorMatrix>'
    f'<feComposite in="d" in2="ga" operator="in"></feComposite></filter>' for n in (1, 2, 3)) + "</defs></svg>"

# The six room shapes, sketched the same way (perimeter only), in the 1000×700 plan space.
ROOM_SHAPES = [
    ("rettangolare", "Rettangolare", {"poly": [(150, 120), (850, 120), (850, 580), (150, 580)]}),
    ("elle", "A L", {"poly": [(150, 100), (560, 100), (560, 370), (850, 370), (850, 600), (150, 600)]}),
    ("rombo", "Romboidale", {"poly": [(500, 70), (820, 350), (500, 630), (180, 350)]}),
    ("quadrata", "Quadrata", {"poly": [(270, 120), (730, 120), (730, 580), (270, 580)]}),
    ("ovale", "Ovale", {"ellipse": (500, 350, 390, 240)}),
    ("cerchio", "A cerchio", {"ellipse": (500, 340, 270, 270)}),
]
def _ellipse_pass(rng, cx, cy, rx, ry, S, w, op):
    import math
    rx *= 1 + rng.uniform(-0.025, 0.025); ry *= 1 + rng.uniform(-0.025, 0.025)
    cx += rng.uniform(-0.8, 0.8) * S; cy += rng.uniform(-0.8, 0.8) * S
    rot = math.radians(rng.uniform(-2.5, 2.5)); start = rng.uniform(0, 2 * math.pi); sweep = 2 * math.pi + math.radians(rng.uniform(6, 22))
    k1, k2, ph = rng.uniform(1.0, 1.8) * S, rng.uniform(0.2, 0.45) * S, rng.uniform(0, 6.28)
    pts = []
    for i in range(73):
        t = start + sweep * i / 72
        wob = k1 * math.sin(2 * t + ph) + k2 * math.sin(5 * t + 2 * ph)
        x, y = (rx + wob) * math.cos(t), (ry + wob) * math.sin(t)
        pts.append((cx + x * math.cos(rot) - y * math.sin(rot), cy + x * math.sin(rot) + y * math.cos(rot)))
    d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    return f'<path d="{d}" stroke-width="{w * S:.2f}" opacity="{op:.2f}"></path>'
def room_sketch(key, geo, label):
    import random
    S = 8
    takes = []
    for n in (1, 2, 3):
        rng = random.Random(f"room-{key}-{n}")
        parts = []
        if "poly" in geo:
            parts += _passes(rng, geo["poly"], True, S, jit=0.3)
        else:
            cx, cy, rx, ry = geo["ellipse"]
            for k in range(rng.choice((2, 3, 3))):
                parts.append(_ellipse_pass(rng, cx, cy, rx, ry, S, rng.uniform(0.8, 1.5) if k == 0 else rng.uniform(0.5, 0.9),
                                           rng.uniform(0.75, 0.95) if k == 0 else rng.uniform(0.35, 0.6)))
        takes.append(f'<g class="boil b{n}" filter="url(#skr{n})" stroke="#EFE8DC">' + "".join(parts) + "</g>")
    return (f'<svg viewBox="0 0 1000 700" width="100%" fill="none" stroke-linecap="round" role="img" aria-label="Pianta {label}" style="display: block">'
            + "".join(takes) + "</svg>")
ROOM_FILTERS = '<svg width="0" height="0" style="position: absolute" aria-hidden="true"><defs>' + "".join(
    f'<filter id="skr{n}" x="-10%" y="-10%" width="120%" height="120%">'
    f'<feTurbulence type="fractalNoise" baseFrequency="0.006" numOctaves="2" seed="{n * 5}" result="w"></feTurbulence>'
    f'<feDisplacementMap in="SourceGraphic" in2="w" scale="13" xChannelSelector="R" yChannelSelector="G" result="d"></feDisplacementMap>'
    f'<feTurbulence type="fractalNoise" baseFrequency="0.14" numOctaves="1" seed="{n * 11}" result="g"></feTurbulence>'
    f'<feColorMatrix in="g" type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 -0.9 1.45" result="ga"></feColorMatrix>'
    f'<feComposite in="d" in2="ga" operator="in"></feComposite></filter>' for n in (1, 2, 3)) + "</defs></svg>"
def room_tiles():
    out = []
    for i, (key, name, geo) in enumerate(ROOM_SHAPES):
        sv = ' data-suono="3"' if i == 0 else ""
        out.append(f'''            <button type="button" class="gl free ptile" style="--d: {450 + i * 60}ms"{sv} onClick="{{{{ pick.go.{key.replace('-', '_')} }}}}">
              {room_sketch(key, geo, name)}
              <span class="dsp" style="font-size: 18px; line-height: 1.1; text-align: center">{name}</span>
            </button>''')
    return "\n".join(out)


# The four staircases, sketched like the rooms: walls in two or three loose passes, treads in one lighter pass.
import math as _m
def _radial(cx, cy, r1x, r1y, r2x, r2y, n, phase=0.0):
    return [[(cx + r1x * _m.cos(t), cy + r1y * _m.sin(t)), (cx + r2x * _m.cos(t), cy + r2y * _m.sin(t))]
            for t in ((i + phase) / n * 2 * _m.pi for i in range(n))]
# "well": the open stairwell; "below": the lower flights glimpsed through it, smaller, a little lower and much
# fainter; "shade": a few light strokes for the depth of the well.
STAIR_SHAPES = [
    ("scala-dritta", "Dritta", {"lines": [[(200, 250), (800, 250)], [(200, 450), (800, 450)]],
                                "treads": [[(200 + i * 50, 250), (200 + i * 50, 450)] for i in range(1, 12)]}),
    ("scala-angoli", "Ad angoli retti", {
        "lines": [[(200, 120), (800, 120), (800, 580), (200, 580)], [(200, 295), (640, 295), (640, 405), (200, 405)]],
        "treads": [[(200 + i * 50, 120), (200 + i * 50, 295)] for i in range(1, 9)] + [[(200 + i * 50, 405), (200 + i * 50, 580)] for i in range(1, 9)],
        "below": [[(232 + i * 46, 312), (232 + i * 46, 340)] for i in range(0, 8)] + [[(232 + i * 46, 362), (232 + i * 46, 390)] for i in range(0, 8)] + [[(214, 351), (590, 351)]],
        "shade": [[(214 + i * 56, 398), (240 + i * 56, 302)] for i in range(7)]}),
    ("chiocciola", "A chiocciola", {
        "ellipses": [(500, 350, 270, 270), (500, 350, 100, 100)],
        "treads": _radial(500, 350, 104, 104, 266, 266, 16),
        "below_ellipses": [(500, 362, 58, 58)],
        "below": _radial(500, 362, 60, 60, 92, 92, 16, 0.5),
        "shade": [[(468 + i * 16, 398), (482 + i * 16, 326)] for i in range(5)]}),
    ("scala-ovale", "Ovale", {
        "ellipses": [(500, 350, 400, 260), (500, 350, 225, 115)],
        "treads": _radial(500, 350, 230, 120, 396, 256, 20),
        "below_ellipses": [(500, 362, 140, 64)],
        "below": _radial(500, 362, 144, 66, 218, 108, 20, 0.5),
        "shade": [[(420 + i * 32, 400), (446 + i * 32, 318)] for i in range(6)]}),
]
def stair_sketch(key, geo, label):
    import random
    S = 8
    takes = []
    for n in (1, 2, 3):
        rng = random.Random(f"stair-{key}-{n}")
        parts = []
        for pts in geo.get("lines", []):
            parts += _passes(rng, pts, False, S, jit=0.3)
        for cx, cy, rx, ry in geo.get("ellipses", []):
            for k in range(rng.choice((2, 3, 3))):
                parts.append(_ellipse_pass(rng, cx, cy, rx, ry, S, rng.uniform(0.8, 1.5) if k == 0 else rng.uniform(0.5, 0.9),
                                           rng.uniform(0.75, 0.95) if k == 0 else rng.uniform(0.35, 0.6)))
        for pts in geo.get("treads", []):
            parts.append(_chain_pass(rng, pts, False, S, rng.uniform(0.5, 0.8), rng.uniform(0.35, 0.55), jit=0.3))
        for cx, cy, rx, ry in geo.get("below_ellipses", []):
            parts.append(_ellipse_pass(rng, cx, cy, rx, ry, S, 0.55, 0.42))
        for pts in geo.get("below", []):
            parts.append(_chain_pass(rng, pts, False, S, rng.uniform(0.45, 0.6), rng.uniform(0.3, 0.42), jit=0.3))
        for pts in geo.get("shade", []):
            parts.append(_chain_pass(rng, pts, False, S, 0.4, rng.uniform(0.12, 0.2), jit=0.3))
        takes.append(f'<g class="boil b{n}" filter="url(#skr{n})" stroke="#EFE8DC">' + "".join(parts) + "</g>")
    return (f'<svg viewBox="0 0 1000 700" width="100%" fill="none" stroke-linecap="round" stroke-linejoin="round" role="img" aria-label="Scala {label}" style="display: block">'
            + "".join(takes) + "</svg>")
def stair_tiles():
    out = []
    for i, (key, name, geo) in enumerate(STAIR_SHAPES):
        sv = ' data-suono="3"' if i == 0 else ""
        out.append(f"""            <button type="button" class="gl free ptile" style="--d: {450 + i * 60}ms"{sv} onClick="{{{{ pick.go.{key.replace('-', '_')} }}}}">
              {stair_sketch(key, geo, name)}
              <span class="dsp" style="font-size: 18px; line-height: 1.1; text-align: center">{name}</span>
            </button>""")
    return "\n".join(out)

def tile(key, name, sub, d, suono=""):
    s = f' data-suono="{suono}"' if suono else ""
    return f'''        <button type="button" class="gl free tile" style="--d: {d}ms"{s} onClick="{{{{ space.{key} }}}}">
          {sketch_icon(key)}
          <span style="display: flex; flex-direction: column; gap: 6px"><span class="dsp" style="font-size: 26px; line-height: 1">{name}</span><span class="lab" style="font-size: 9px; color: rgba(243,235,221,.85)">{sub}</span></span>
        </button>'''

def h1(prefix, d1=200, d2=310, size=40):
    return f'''      <h1 class="dsp" style="margin: 10px 0 0; font-size: {size}px; line-height: 1.04; letter-spacing: -.012em">
        <span class="posa" style="--d: {d1}ms"><span data-suono="1" style="display: block">{{{{ {prefix}.t1 }}}}</span></span>
        <span class="posa" style="--d: {d2}ms"><span data-suono="2" style="display: block"><em>{{{{ {prefix}.t2 }}}}</em></span></span>
      </h1>'''

def crumb(text_hole, d=100, mt=28, right=""):
    r = f'<span class="dsp" style="font-size: 15px; font-style: italic; color: #D9C29A">{right}</span>' if right else ""
    return f'''      <div class="posa" style="--d: {d}ms; margin-top: {mt}px">
        <div style="display: flex; justify-content: space-between; align-items: baseline"><span class="lab" style="color: #D9C29A">{text_hole}</span>{r}</div>
      </div>'''

PRIMARY = lambda label, handler, d, suono="", rec=False: f'''        <div class="posa" style="--d: {d}ms; flex: 2; display: flex">
          <button type="button"{f' data-suono="{suono}"' if suono else ''} class="btn btn-p" style="flex: 1" onClick="{{{{ {handler} }}}}">{b.REC_DOT if rec else ''}{label}</button>
        </div>'''
GHOST = lambda label, handler, d: f'''        <button type="button" class="gl free btn" style="--d: {d}ms; flex: 1" onClick="{{{{ {handler} }}}}">{label}</button>'''

FP_SWITCH = '''              <div style="margin-top: 12px; display: flex; gap: 6px; align-items: center">
                <div role="group" aria-label="Vista" style="display: flex; gap: 4px">
                  <button type="button" class="pill seg-btn" aria-pressed="{{ step.planOn }}" onClick="{{ step.showPlan }}">Pianta</button>
                  <button type="button" class="pill seg-btn" aria-pressed="{{ step.fpOn }}" onClick="{{ step.showFp }}">Prima persona</button>
                </div>
              </div>
'''

SCREENS = f'''<sc-if value="{{{{ isSetup }}}}" hint-placeholder-val="{{{{ true }}}}">
      <main style="flex: 1; display: flex; flex-direction: column; min-height: 0">
        <div class="posa" style="--d: 100ms; margin-top: 30px">
          <div style="display: flex; flex-direction: column; gap: 12px">
            <div style="display: flex; justify-content: space-between; align-items: baseline">
              <span class="lab" style="color: rgba(243,235,221,.78)">Prima di iniziare</span>
              <span class="dsp" style="font-size: 15px; font-style: italic; color: #D9C29A">{{{{ setup.passo }}}}</span>
            </div>
            <div aria-hidden="true" style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 6px">
              <sc-for list="{{{{ setup.segs }}}}" as="g" hint-placeholder-count="3"><span class="{{{{g.cls}}}}" style="--d: 520ms; height: 2px; background: {{{{g.bg}}}}"></span></sc-for>
            </div>
          </div>
        </div>
        <sc-if value="{{{{ setup.kicker }}}}" hint-placeholder-val="{{{{ true }}}}">
        <div class="posa" style="--d: 150ms; margin-top: 26px">
          <p class="lab" style="margin: 0; display: flex; align-items: center; gap: 10px; color: #D9C29A"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="{{{{ setup.icon }}}}"></path></svg>{{{{ setup.kicker }}}}</p>
        </div>
        </sc-if>
        <sc-if value="{{{{ setup.noKicker }}}}" hint-placeholder-val="{{{{ false }}}}"><div style="height: 18px"></div></sc-if>
{h1("setup", size=46)}
        <sc-if value="{{{{ setup.noteTop }}}}" hint-placeholder-val="{{{{ false }}}}">
        <div class="posa" style="--d: 450ms; margin: 16px 2px 0">
          <p style="margin: 0; display: flex; gap: 12px; align-items: flex-start; font-size: 13px; line-height: 1.5; color: rgba(243,235,221,.9)">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#D9C29A" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" style="flex: none; margin-top: 1px"><circle cx="12" cy="12" r="10"></circle><path d="M7.5 12.5l3 3 6-6.5"></path></svg>
            <span><span class="lab" style="font-size: 9px; color: #D9C29A">Deve vedersi</span><br>{{{{ setup.note }}}}</span>
          </p>
        </div>
        </sc-if>
        <sc-if value="{{{{ setup.lead }}}}" hint-placeholder-val="{{{{ true }}}}">
        <div class="posa" style="--d: 450ms; margin-top: 14px">
          <p data-suono="3" style="margin: 0; font-size: 15px; line-height: 1.55; color: rgba(243,235,221,.9); max-width: 33ch">{{{{ setup.lead }}}}</p>
        </div>
        </sc-if>
        <div class="posa l" style="--d: 590ms; margin-top: 22px">
          <section ref="{{{{ fig.ref }}}}" data-suono="4" class="lg" style="border-radius: 22px; padding: 18px 20px 8px; --h: {{{{fig.h}}}}">
            {b.glass_layers("fig")}
            <div class="lg-c">
              <h2 class="lab" style="margin: 0 0 6px; color: rgba(243,235,221,.82)">Come farlo</h2>
              <ol style="list-style: none; margin: 0; padding: 0">
                <sc-for list="{{{{ setup.items }}}}" as="it" hint-placeholder-count="3"><li class="li-row" style="padding: 10px 0"><span class="dsp" style="font-style: italic; font-size: 17px; color: #D9C29A">{{{{ it.n }}}}</span><span>{{{{ it.t }}}}</span></li></sc-for>
              </ol>
            </div>
          </section>
        </div>
        <sc-if value="{{{{ setup.noteBottom }}}}" hint-placeholder-val="{{{{ true }}}}">
        <div class="posa" style="--d: 650ms; margin: 16px 2px 0">
          <p style="margin: 0; display: flex; gap: 12px; align-items: flex-start; font-size: 13px; line-height: 1.5; color: rgba(243,235,221,.9)">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#D9C29A" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" style="flex: none; margin-top: 1px"><circle cx="12" cy="12" r="10"></circle><path d="M7.5 12.5l3 3 6-6.5"></path></svg>
            <span><span class="lab" style="font-size: 9px; color: #D9C29A">Deve vedersi</span><br>{{{{ setup.note }}}}</span>
          </p>
        </div>
        </sc-if>
        <nav style="margin-top: auto; display: flex; gap: 10px">
          <sc-if value="{{{{ setup.hasBack }}}}" hint-placeholder-val="{{{{ false }}}}">
          <div class="posa" style="--d: 710ms; flex: 1; display: flex">
            <button ref="{{{{ back.ref }}}}" type="button" class="btn lg" style="flex: 1; --h: {{{{back.h}}}}" onClick="{{{{ goBack }}}}">
              {b.glass_layers("back")}
              <span class="lg-c">Indietro</span>
            </button>
          </div>
          </sc-if>
{PRIMARY("{{ setup.primary }}", "setup.next", 760, "")}
        </nav>
      </main>
    </sc-if>

    <sc-if value="{{{{ isPerm }}}}" hint-placeholder-val="{{{{ false }}}}">
      <main style="flex: 1; display: flex; flex-direction: column; min-height: 0">
        <div class="posa" style="--d: 100ms; margin-top: 34px">
          <p class="lab" style="margin: 0; color: #D9C29A">Un’ultima cosa</p>
        </div>
        <h1 class="dsp" style="margin: 12px 0 0; font-size: 44px; line-height: 1.02; letter-spacing: -.012em">
          <span class="posa" style="--d: 200ms"><span data-suono="1" style="display: block">La fotocamera,</span></span>
          <span class="posa" style="--d: 310ms"><span data-suono="2" style="display: block"><em>qui dentro</em></span></span>
        </h1>
        <div class="posa" style="--d: 450ms; margin-top: 14px">
          <p data-suono="3" style="margin: 0; font-size: 15px; line-height: 1.55; color: #F3EBDD; max-width: 34ch">La guida registra al suo interno: niente app da aprire, niente andirivieni.</p>
        </div>
        <div class="posa l" style="--d: 590ms; margin-top: 20px">
          <section ref="{{{{ fig.ref }}}}" data-suono="4" class="lg" style="border-radius: 22px; padding: 6px 20px; --h: {{{{fig.h}}}}">
            {b.glass_layers("fig")}
            <div class="lg-c">
              <div class="irow">
                <span class="irow-i"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 8h3l2-2.5h6L17 8h3v11H4z"></path><circle cx="12" cy="13.5" r="3.5"></circle></svg></span>
                <span style="display: flex; flex-direction: column; gap: 4px"><span class="irow-t">Fotocamera</span><span class="irow-p">Per riprendere gli spazi con la lente 0,5×. Solo le immagini: il microfono resta spento.</span></span>
              </div>
              <div class="irow">
                <span class="irow-i"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4.5 12a7.5 7.5 0 0 1 13-5.1M19.5 12a7.5 7.5 0 0 1-13 5.1"></path><path d="M17.5 3.5v3.5H14M6.5 20.5V17H10"></path></svg></span>
                <span style="display: flex; flex-direction: column; gap: 4px"><span class="irow-t">Movimento</span><span class="irow-p">Per sapere quanto hai girato: ogni ripresa si ferma da sola.</span></span>
              </div>
            </div>
          </section>
        </div>
        <div class="posa" style="--d: 650ms; margin-top: 16px">
          <p style="margin: 0; font-size: 13px; line-height: 1.55; color: #F3EBDD; max-width: 34ch">Il telefono può chiederti uno o due permessi: tocca sempre «Consenti».</p>
        </div>
        <nav style="margin-top: auto; display: flex; gap: 10px">
          <div class="posa" style="--d: 710ms; flex: 1; display: flex">
            <button ref="{{{{ back.ref }}}}" type="button" class="btn lg" style="flex: 1; --h: {{{{back.h}}}}" onClick="{{{{ goBack }}}}">
              {b.glass_layers("back")}
              <span class="lg-c">Indietro</span>
            </button>
          </div>
{PRIMARY("Consenti", "perm.allow", 760, "")}
        </nav>
      </main>
    </sc-if>

    <sc-if value="{{{{ isSpace }}}}" hint-placeholder-val="{{{{ false }}}}">
      <main style="flex: 1; display: flex; flex-direction: column; min-height: 0">
{crumb("{{ space.crumb }}")}
      <h1 class="dsp" style="margin: 10px 0 0; font-size: 40px; line-height: 1.04; letter-spacing: -.012em">
        <span class="posa" style="--d: 200ms"><span data-suono="1" style="display: block">Cosa riprendi</span></span>
        <span class="posa" style="--d: 310ms"><span data-suono="2" style="display: block"><em>adesso?</em></span></span>
      </h1>
        {SKETCH_FILTERS}
        <div style="margin-top: 22px; display: flex; flex-direction: column; gap: 10px">
{tile("ambiente", "Ambiente", "Stanze e spazi aperti", 450, "3")}
{tile("corridoio", "Corridoio", "Collegamenti tra gli spazi", 510)}
{tile("scala", "Scalinata", "Scale di ogni forma", 570)}
        </div>
        <nav style="margin-top: auto; display: flex; flex-direction: column; gap: 10px">
          <!-- Just finished a space: its last take can be done again, as with Rifai on the camera screen. -->
          <sc-if value="{{{{ space.hasRedo }}}}" hint-placeholder-val="{{{{ false }}}}">
            <button type="button" class="gl free btn" style="--d: 560ms; display: flex; align-items: center; justify-content: center; gap: 8px" onClick="{{{{ space.redo }}}}">{REDO}<span>{{{{ space.redoLabel }}}}</span></button>
          </sc-if>
          <button type="button" data-suono="4" class="gl free btn" style="--d: 590ms" onClick="{{{{ space.finish }}}}">Ho finito la casa</button>
        </nav>
      </main>
    </sc-if>

    <sc-if value="{{{{ isPick }}}}" hint-placeholder-val="{{{{ false }}}}">
      <main style="flex: 1; display: flex; flex-direction: column; min-height: 0">
{crumb("{{ pick.crumb }}")}
{h1("pick")}
        <sc-if value="{{{{ pick.rooms }}}}" hint-placeholder-val="{{{{ true }}}}">
          {ROOM_FILTERS}
          <div style="margin-top: 20px; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px">
{room_tiles()}
          </div>
        </sc-if>
        <sc-if value="{{{{ pick.stairs }}}}" hint-placeholder-val="{{{{ false }}}}">
          {ROOM_FILTERS}
          <div style="margin-top: 20px; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px">
{stair_tiles()}
          </div>
        </sc-if>
      </main>
    </sc-if>

    <sc-if value="{{{{ isStep }}}}" hint-placeholder-val="{{{{ false }}}}">
      <main style="flex: 1; display: flex; flex-direction: column; min-height: 0">
        <div class="posa" style="--d: 100ms; margin-top: 30px">
          <div style="display: flex; flex-direction: column; gap: 12px">
            <div style="display: flex; justify-content: space-between; align-items: baseline">
              <span class="lab" style="color: rgba(243,235,221,.78)">{{{{ step.area }}}}</span>
              <span class="dsp" style="font-size: 15px; font-style: italic; color: #D9C29A">{{{{ step.passo }}}}</span>
            </div>
            <div aria-hidden="true" style="display: grid; grid-template-columns: repeat({{{{step.n}}}}, minmax(0, 1fr)); gap: 5px">
              <sc-for list="{{{{ step.segs }}}}" as="g" hint-placeholder-count="8"><span class="{{{{g.cls}}}}" style="--d: 520ms; height: 2px; background: {{{{g.bg}}}}"></span></sc-for>
            </div>
          </div>
        </div>
        <!-- How to film the step (kicker and the i. / ii. actions) is shown in the Registra sheet, not here. -->
        <div style="height: 16px"></div>
{h1("step", size=44)}
        <div class="posa l" style="--d: 450ms; --d0: 1350ms; margin-top: 20px">
          <figure ref="{{{{ fig.ref }}}}" data-suono="3" class="lg" style="margin: 0; border-radius: 22px; padding: 14px; --h: {{{{fig.h}}}}">
            {b.glass_layers("fig")}
            <div class="lg-c">
              <!-- Plan and first-person view stacked in the same place, so both keep the same clock; one is shown. -->
              <div class="views {{{{ step.view }}}}">
          {plan_html("step.plan")}
          <div class="fp-view" role="img" aria-label="{{{{ step.fp.label }}}}">
            <svg viewBox="0 0 1000 700" width="100%" aria-hidden="true" style="display: block">
              <defs><filter id="fpk1" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency="0.008" numOctaves="2" seed="7" result="w"></feTurbulence><feDisplacementMap in="SourceGraphic" in2="w" scale="10" xChannelSelector="R" yChannelSelector="G" result="d"></feDisplacementMap><feTurbulence type="fractalNoise" baseFrequency="0.12" numOctaves="1" seed="13" result="g"></feTurbulence><feColorMatrix in="g" type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 -0.9 1.45" result="ga"></feColorMatrix><feComposite in="d" in2="ga" operator="in"></feComposite></filter><filter id="fpk2" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency="0.008" numOctaves="2" seed="14" result="w"></feTurbulence><feDisplacementMap in="SourceGraphic" in2="w" scale="10" xChannelSelector="R" yChannelSelector="G" result="d"></feDisplacementMap><feTurbulence type="fractalNoise" baseFrequency="0.12" numOctaves="1" seed="26" result="g"></feTurbulence><feColorMatrix in="g" type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 -0.9 1.45" result="ga"></feColorMatrix><feComposite in="d" in2="ga" operator="in"></feComposite></filter><filter id="fpk3" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency="0.008" numOctaves="2" seed="21" result="w"></feTurbulence><feDisplacementMap in="SourceGraphic" in2="w" scale="10" xChannelSelector="R" yChannelSelector="G" result="d"></feDisplacementMap><feTurbulence type="fractalNoise" baseFrequency="0.12" numOctaves="1" seed="39" result="g"></feTurbulence><feColorMatrix in="g" type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 -0.9 1.45" result="ga"></feColorMatrix><feComposite in="d" in2="ga" operator="in"></feComposite></filter></defs>
              <g class="fp-move {{{{ step.fp.mode }}}}" style="--sx: {{{{ step.fp.sx }}}}; --zoom: {{{{ step.fp.zoom }}}}; --rdur: {{{{ step.plan.rdur }}}}; --wdur: {{{{ step.plan.wdur }}}}; --wait: {{{{ step.plan.wait }}}}">
                <path d="{{{{ step.fp.floor }}}}" fill="rgba(18,15,9,.16)"></path>
                <path d="{{{{ step.fp.wall }}}}" fill="rgba(18,15,9,.26)"></path>
                <g class="boil b1" filter="url(#fpk1)" fill="none" stroke="#EFE8DC" stroke-linecap="round" stroke-linejoin="round"><path d="{{{{ step.fp.lines }}}}" stroke-width="3.2" opacity=".9"></path><path d="{{{{ step.fp.door }}}}" stroke-width="3.2"></path><path d="{{{{ step.fp.fine }}}}" stroke-width="2" opacity=".55"></path></g><g class="boil b2" filter="url(#fpk2)" fill="none" stroke="#EFE8DC" stroke-linecap="round" stroke-linejoin="round"><path d="{{{{ step.fp.lines }}}}" stroke-width="3.2" opacity=".9"></path><path d="{{{{ step.fp.door }}}}" stroke-width="3.2"></path><path d="{{{{ step.fp.fine }}}}" stroke-width="2" opacity=".55"></path></g><g class="boil b3" filter="url(#fpk3)" fill="none" stroke="#EFE8DC" stroke-linecap="round" stroke-linejoin="round"><path d="{{{{ step.fp.lines }}}}" stroke-width="3.2" opacity=".9"></path><path d="{{{{ step.fp.door }}}}" stroke-width="3.2"></path><path d="{{{{ step.fp.fine }}}}" stroke-width="2" opacity=".55"></path></g>
              </g>
              <g fill="none" stroke="rgba(243,235,221,.8)" stroke-width="3" stroke-linecap="round">
                <path d="M40,90 V40 H90 M910,40 H960 V90 M960,610 V660 H910 M90,660 H40 V610"></path>
                <path d="M486,350 H514 M500,336 V364" stroke-width="2.4" opacity=".7"></path>
              </g>
            </svg>
          </div>
              </div>
              <!-- The first-person view is off for now: the Pianta / Prima persona switch (FP_SWITCH in build_proto.py) brings it back. -->
            </div>
          </figure>
        </div>
        <!-- Skipping a point: its own row in the free space under the plan, big enough to be seen. -->
        <sc-if value="{{{{ step.isTurn }}}}" hint-placeholder-val="{{{{ false }}}}">
          <div style="flex: 1; display: flex; align-items: center; padding: 18px 0">
            <div class="posa" style="--d: 520ms; width: 100%">
              <button type="button" class="skip-btn" onClick="{{{{ step.skip }}}}"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#D9C29A" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 5.5l7 6.5-7 6.5M12.5 5.5l7 6.5-7 6.5"></path></svg><span>Salta, punto troppo stretto<br>o ostruito da un oggetto</span></button>
            </div>
          </div>
        </sc-if>
        <nav style="margin-top: auto; display: flex; gap: 10px">
          <div class="posa" style="--d: 560ms; flex: 1; display: flex">
            <button ref="{{{{ back.ref }}}}" type="button" class="btn lg" style="flex: 1; --h: {{{{back.h}}}}" onClick="{{{{ goBack }}}}">
              {b.glass_layers("back")}
              <span class="lg-c">Indietro</span>
            </button>
          </div>
{PRIMARY("Registra", "step.rec", 590, "4", rec=True)}
        </nav>
      </main>
    </sc-if>

    <sc-if value="{{{{ isDone }}}}" hint-placeholder-val="{{{{ false }}}}">
      <main style="flex: 1; display: flex; flex-direction: column; min-height: 0">
{crumb("Fatto", 100, 96)}
      <h1 class="dsp" style="margin: 14px 0 0; font-size: 60px; line-height: .98; letter-spacing: -.015em">
        <span class="posa" style="--d: 200ms"><span data-suono="1" style="display: block">Spazio</span></span>
        <span class="posa" style="--d: 310ms"><span data-suono="2" style="display: block"><em>finito.</em></span></span>
      </h1>
        <div class="posa" style="--d: 450ms; margin-top: 22px">
          <p data-suono="3" style="margin: 0; font-size: 15px; line-height: 1.55">Hai ripreso tutti i passi di questo spazio.</p>
        </div>
        <nav style="margin-top: auto; display: flex; flex-direction: column; gap: 10px">
          <div class="posa" style="--d: 590ms; display: flex">
            <button type="button" data-suono="4" class="btn btn-p" style="flex: 1" onClick="{{{{ done.another }}}}">Riprendi un altro spazio</button>
          </div>
          <button type="button" class="gl free btn" style="--d: 650ms" onClick="{{{{ done.finish }}}}">Ho finito la casa</button>
        </nav>
      </main>
    </sc-if>

    <sc-if value="{{{{ isEnd }}}}" hint-placeholder-val="{{{{ false }}}}">
      <main style="flex: 1; display: flex; flex-direction: column; min-height: 0">
{crumb("Alla fine", 100, 96)}
      <h1 class="dsp" style="margin: 14px 0 0; font-size: 60px; line-height: .98; letter-spacing: -.015em">
        <span class="posa" style="--d: 200ms"><span data-suono="1" style="display: block">Carica</span></span>
        <span class="posa" style="--d: 310ms"><span data-suono="2" style="display: block"><em>i video</em></span></span>
      </h1>
        <div class="posa" style="--d: 450ms; margin-top: 22px">
          <p data-suono="3" style="margin: 0; font-size: 15px; line-height: 1.55">Qui la guida carica i video registrati.</p>
        </div>
        <nav style="margin-top: auto; display: flex; gap: 10px">
          <div class="posa" style="--d: 590ms; flex: 1; display: flex">
            <button type="button" data-suono="4" class="btn btn-p" style="flex: 1" onClick="{{{{ end.restart }}}}">Ricomincia il prototipo</button>
          </div>
        </nav>
      </main>
    </sc-if>'''

REC = f'''  <sc-if value="{{{{ isRec }}}}" hint-placeholder-val="{{{{ false }}}}">
    <div class="rec-screen avv-{{{{ rec.avv }}}} {{{{ rec.mode }}}}" style="position: absolute; inset: 0; z-index: 5; background: radial-gradient(120% 70% at 60% 38%, #6b5a43 0%, #3d3327 45%, #1c1812 100%)">
      <!-- The camera's picture goes under everything here; in the canvas a sketch stands in for it. -->
      <svg class="cam-ph" aria-hidden="true" viewBox="0 0 390 844" width="390" height="844" style="position: absolute; inset: 0">
        <path d="M0 210 L150 300 L150 560 L0 690 M390 170 L262 292 L262 568 L390 720 M150 300 L262 292 M150 560 L262 568" fill="none" stroke="rgba(243,235,221,.10)" stroke-width="1.2"></path>
      </svg>
      <p class="lab cam-ph" style="position: absolute; left: 0; right: 0; top: 470px; margin: 0; text-align: center; font-size: 9px; color: rgba(243,235,221,.5)">Fotocamera · è già la vista in prima persona</p>
      <sc-if value="{{{{ rec.guide }}}}" hint-placeholder-val="{{{{ true }}}}">
        <section class="gl free mini" style="--d: 0ms; position: absolute; left: 12px; right: 12px; top: 54px; border-radius: 22px; padding: 10px; display: grid; grid-template-columns: 132px 1fr; gap: 12px; align-items: center">
          {plan_html("rec.plan")}
          <div style="display: flex; flex-direction: column; gap: 6px; padding-right: 40px">
            <span class="lab" style="font-size: 9px">{{{{ rec.passo }}}}</span>
            <p style="margin: 0; font-size: 14px; line-height: 1.45">{{{{ rec.text }}}}</p>
          </div>
          <button type="button" aria-label="Nascondi la guida" onClick="{{{{ rec.hide }}}}" style="position: absolute; top: 4px; right: 4px; width: 44px; height: 44px; display: grid; place-items: center; color: #F3EBDD">{CLOSE}</button>
        </section>
      </sc-if>
      <sc-if value="{{{{ rec.noGuide }}}}" hint-placeholder-val="{{{{ false }}}}">
        <button type="button" class="gl free" style="--d: 0ms; position: absolute; top: 54px; left: 12px; height: 44px; padding: 0 18px; border-radius: 999px" onClick="{{{{ rec.show }}}}"><span class="lab">Mostra guida</span></button>
      </sc-if>
      <!-- Live guidance: the reticle in the middle shows how far to turn or walk, the level, and one warning at a time. -->
      <sc-if value="{{{{ rec.live }}}}" hint-placeholder-val="{{{{ true }}}}">
      <div style="position: absolute; left: 0; right: 0; top: 300px; height: 200px; display: grid; place-items: center; pointer-events: none">
        <div class="level" aria-hidden="true" style="position: absolute; left: 0; right: 0; top: 99px; height: 2px">
          <span class="lv" style="position: absolute; left: 22px; width: 64px; height: 2px"></span>
          <span class="lv" style="position: absolute; right: 22px; width: 64px; height: 2px"></span>
        </div>
      </div>
      <!-- Follow the arrow (turns only), set in the room: the dashed line starts where the phone points when the take
           starts and runs the whole turn; the arrow travels it at the right pace. Turning at that pace keeps the arrow in
           the ring in the middle. In the guide the motion sensors move line and arrow; here they show the idea. -->
      <sc-if value="{{{{ rec.isTurn }}}}" hint-placeholder-val="{{{{ true }}}}">
        <div class="aim" role="img" aria-label="{{{{ rec.trailText }}}}" style="--rdur: {{{{ rec.rdur }}}}">
          <div class="aim-world" style="--len: {{{{ rec.aimLen }}}}">
            <span class="aim-line"></span>
            <span class="aim-end"></span>
            <span class="aim-arrow"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#17130C" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h13M13 6.5l5.5 5.5-5.5 5.5"></path></svg></span>
          </div>
          <span class="aim-you"></span>
        </div>
      </sc-if>
      <div aria-live="polite" style="position: absolute; left: 0; right: 0; bottom: 210px; height: 44px; display: grid; place-items: center; pointer-events: none">
        <span class="chip chip-ok gl"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"></path></svg>Velocità giusta</span>
        <span class="chip chip-piano"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8 5v14M16 5v14"></path></svg>Più piano</span>
        <span class="chip chip-dritto"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M3 12h7M14 12h7"></path><circle cx="12" cy="12" r="2"></circle></svg>Tieni il telefono dritto</span>
        <span class="chip chip-luce gl"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="4"></circle><path d="M12 2v2M12 20v2M2 12h2M20 12h2"></path></svg>Poca luce: accendi le luci</span>
      </div>
      <div class="gl free" style="--d: 120ms; position: absolute; left: 50%; margin-left: -50px; width: 100px; bottom: 146px; height: 40px; border-radius: 999px; display: flex; align-items: center; justify-content: center; gap: 9px; font-size: 14px; font-weight: 600; font-variant-numeric: tabular-nums"><span class="rec-dot" aria-hidden="true" style="width: 9px; height: 9px; border-radius: 50%; background: #E0583F"></span><span class="rec-clock">{{{{ rec.clock }}}}</span></div>
      <button type="button" class="stop" aria-label="Ferma la registrazione" onClick="{{{{ rec.stop }}}}"><span style="width: 30px; height: 30px; border-radius: 8px; background: #E0583F"></span></button>
      </sc-if>
      <!-- Ready: the camera stays on between one step and the next. Go to the point and press the red button. -->
      <sc-if value="{{{{ rec.ready }}}}" hint-placeholder-val="{{{{ false }}}}">
        <sc-if value="{{{{ rec.hasNote }}}}" hint-placeholder-val="{{{{ false }}}}">
          <div aria-live="polite" style="position: absolute; left: 16px; right: 16px; bottom: 206px; display: flex; justify-content: center; pointer-events: none"><span class="chip chip-note">{{{{ rec.note }}}}</span></div>
        </sc-if>
        <sc-if value="{{{{ rec.hasRedo }}}}" hint-placeholder-val="{{{{ false }}}}">
          <div style="position: absolute; left: 16px; right: 16px; bottom: 146px; display: flex; justify-content: center">
            <button type="button" class="gl free rec-pill" style="--d: 80ms" onClick="{{{{ rec.redo }}}}">{REDO}<span>{{{{ rec.redoLabel }}}}</span></button>
          </div>
        </sc-if>
        <button type="button" class="gl free rec-pill rec-side" style="--d: 40ms; left: 16px" onClick="{{{{ rec.toPlan }}}}">{PLAN_I}<span>Pianta</span></button>
        <button type="button" class="recb" aria-label="Registra" onClick="{{{{ rec.start }}}}"><span></span></button>
        <sc-if value="{{{{ rec.canShape }}}}" hint-placeholder-val="{{{{ false }}}}">
          <div style="position: absolute; left: 16px; right: 16px; bottom: 146px; display: flex; justify-content: center">
            <button type="button" class="gl free rec-pill" style="--d: 80ms" onClick="{{{{ rec.shape }}}}">{SHAPE_I}<span>Cambia forma della stanza</span></button>
          </div>
        </sc-if>
        <sc-if value="{{{{ rec.canSkip }}}}" hint-placeholder-val="{{{{ false }}}}">
          <button type="button" class="gl free rec-pill rec-side" style="--d: 60ms; right: 16px" onClick="{{{{ rec.skip }}}}">{SKIP_I}<span>Salta</span></button>
        </sc-if>
      </sc-if>
    </div>
  </sc-if>'''

BODY = f'''  <div class="scr" style="position: relative; height: 100%; box-sizing: border-box; padding: 54px 20px 34px; display: flex; flex-direction: column">
    <p class="brand" aria-label="Foretaste">FORETASTE</p>
    <header style="display: flex; justify-content: space-between; align-items: center; min-height: 44px">
      <sc-if value="{{{{ hasBack }}}}" hint-placeholder-val="{{{{ false }}}}">
        <button type="button" class="gl free icon-btn" style="--d: 0ms" aria-label="Indietro" onClick="{{{{ goBack }}}}">{CHEV_L}</button>
      </sc-if>
      <sc-if value="{{{{ noBack }}}}" hint-placeholder-val="{{{{ true }}}}">
      {b.LOGO}
      </sc-if>
      <div style="display: flex; gap: 8px">
      <button type="button" class="gl free fb-pill" style="--d: 20ms" onClick="{{{{ fb.open }}}}"><sc-if value="{{{{ fb.ask }}}}" hint-placeholder-val="{{{{ true }}}}">Inviaci un Feedback</sc-if><sc-if value="{{{{ fb.thanked }}}}" hint-placeholder-val="{{{{ false }}}}">Grazie per il feedback!</sc-if><svg width="14" height="14" viewBox="0 0 24 24" fill="#D9C29A" aria-hidden="true"><path d="M12 20.5s-7.5-4.6-7.5-10.2A4.3 4.3 0 0 1 12 7.6a4.3 4.3 0 0 1 7.5 2.7c0 5.6-7.5 10.2-7.5 10.2z"></path></svg></button>
      {b.SND_BTN}
      </div>
    </header>
{SCREENS}
  </div>
{REC}
  <!-- Feedback: a bottom sheet over the screen, a 1–5 star rating and a short note. -->
  <sc-if value="{{{{ fb.isOpen }}}}" hint-placeholder-val="{{{{ false }}}}">
    <div style="position: absolute; inset: 0; z-index: 10">
      <button type="button" aria-label="Chiudi il feedback" onClick="{{{{ fb.close }}}}" style="position: absolute; inset: 0; width: 100%; border: 0; padding: 0; background: rgba(10,8,4,.5); cursor: pointer"></button>
      <section class="gl fb-sheet" role="dialog" aria-modal="true" aria-labelledby="fb-title" style="position: absolute; left: 0; right: 0; bottom: 0; border-radius: 30px 30px 0 0; border-bottom: 0; padding: 26px 22px 34px; display: flex; flex-direction: column; gap: 18px; background: rgba(18,15,9,.42)">
        <div style="display: flex; justify-content: space-between; align-items: flex-start">
          <div style="display: flex; flex-direction: column; gap: 8px">
            <span class="lab" style="color: rgba(243,235,221,.78)">Feedback</span>
            <h2 id="fb-title" class="dsp" style="margin: 0; font-size: 32px; line-height: 1.04; letter-spacing: -.012em">Com’è <span style="font-style: italic; color: #E6D3B0">la guida?</span></h2>
          </div>
          <button type="button" class="gl icon-btn" aria-label="Chiudi" onClick="{{{{ fb.close }}}}"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"></path></svg></button>
        </div>
        <sc-if value="{{{{ fb.form }}}}" hint-placeholder-val="{{{{ true }}}}">
          <div style="display: flex; flex-direction: column; gap: 6px">
            <div role="radiogroup" aria-label="Valutazione della guida, da 1 a 5 stelle" style="display: flex; gap: 4px; margin-left: -7px">
              <sc-for list="{{{{ fb.stars }}}}" as="s" hint-placeholder-count="5"><button type="button" role="radio" class="star" aria-checked="{{{{ s.checked }}}}" aria-label="{{{{ s.label }}}}" onClick="{{{{ s.pick }}}}"><svg width="30" height="30" viewBox="0 0 24 24" fill="{{{{ s.fill }}}}" stroke="#D9C29A" stroke-width="1.3" stroke-linejoin="round" aria-hidden="true"><path d="M12 3.2l2.6 5.5 6 .8-4.4 4.1 1.1 5.9L12 16.6 6.7 19.5l1.1-5.9L3.4 9.5l6-.8z"></path></svg></button></sc-for>
            </div>
            <span class="dsp" aria-live="polite" style="font-size: 17px; font-style: italic; color: #D9C29A; min-height: 22px">{{{{ fb.word }}}}</span>
          </div>
          <div style="display: flex; flex-direction: column; gap: 8px">
            <label for="fb-text" class="lab" style="color: rgba(243,235,221,.85)">Cosa possiamo migliorare?</label>
            <textarea id="fb-text" class="gl fb-text" rows="4" maxLength="{{{{ fb.max }}}}" placeholder="Scrivi qui, se vuoi" value="{{{{ fb.text }}}}" onChange="{{{{ fb.type }}}}"></textarea>
            <span aria-live="polite" style="align-self: flex-end; font-size: 12px; font-variant-numeric: tabular-nums; color: {{{{ fb.countColor }}}}">{{{{ fb.count }}}}</span>
          </div>
          <button type="button" class="btn btn-p" disabled="{{{{ fb.cannot }}}}" style="opacity: {{{{ fb.sendOpacity }}}}" onClick="{{{{ fb.send }}}}">Invia il feedback</button>
        </sc-if>
        <sc-if value="{{{{ fb.sent }}}}" hint-placeholder-val="{{{{ false }}}}">
          <div style="display: flex; flex-direction: column; gap: 10px; padding: 6px 0 4px">
            <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#D9C29A" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9.5"></circle><path d="M7.5 12.3l3 3 6-6.3"></path></svg>
            <p class="dsp" style="margin: 0; font-size: 24px; line-height: 1.2">Grazie. <span style="font-style: italic; color: #E6D3B0">Il tuo parere ci aiuta a migliorare la guida.</span></p>
          </div>
          <button type="button" class="btn btn-p" onClick="{{{{ fb.close }}}}">Chiudi</button>
        </sc-if>
      </section>
    </div>
  </sc-if>'''

FLOW_JS = r"""
// ---- The flow of the prototype, from the "Punti di ripresa" data (30/10). ----
const DATA = __DATA__;
const rad = (d) => d * Math.PI / 180;
const range = (a, b) => Array.from({ length: b - a }, (_, i) => a + i);
const SHAPES = {
  rettangolare: { name: 'Rettangolare', walls: ['M150,120 H850 V580 H150 Z'], door: [[465, 580], [535, 580]] },
  elle: { name: 'A L', walls: ['M150,100 H560 V370 H850 V600 H150 Z'], door: [[315, 600], [385, 600]] },
  rombo: { name: 'Romboidale', walls: ['M500,70 L820,350 L500,630 L180,350 Z'], door: [[318, 471], [362, 509]] },
  quadrata: { name: 'Quadrata', walls: ['M270,120 H730 V580 H270 Z'], door: [[465, 580], [535, 580]] },
  ovale: { name: 'Ovale', ellipse: [500, 350, 390, 240], door: [[465, 589], [535, 589]] },
  cerchio: { name: 'A cerchio', ellipse: [500, 340, 270, 270], door: [[465, 608], [535, 608]] },
  corridoio: { name: 'Corridoio', walls: ['M80,290 H920 V410 H80 Z'], door: [[80, 315], [80, 385]] },
  'scala-dritta': { name: 'Dritta', walls: ['M200,250 H800', 'M200,450 H800'], steps: () => range(1, 12).map((i) => `M${200 + i * 50},250 V450`), labels: [[145, 288, 'giù'], [855, 288, 'su']] },
  'scala-angoli': { name: 'Ad angoli retti', walls: ['M200,120 H800 V580 H200', 'M200,350 H640'], steps: () => [...range(1, 9).map((i) => `M${200 + i * 50},350 V580`), ...range(1, 9).map((i) => `M${200 + i * 50},120 V350`)], labels: [[120, 475, 'giù'], [120, 250, 'su']] },
  chiocciola: { name: 'A chiocciola', ellipse: [500, 350, 270, 270], newel: [500, 350, 34], steps: () => range(0, 16).map((i) => { const a = i / 16 * 2 * Math.PI; return `M${500 + 38 * Math.cos(a)},${350 + 38 * Math.sin(a)} L${500 + 266 * Math.cos(a)},${350 + 266 * Math.sin(a)}`; }), labels: [[500, 668, 'giù'], [578, 562, 'su']] },
  'scala-ovale': { name: 'Ovale', ellipse: [500, 350, 400, 260], inner: [500, 350, 200, 95], steps: () => range(0, 20).map((i) => { const a = i / 20 * 2 * Math.PI; return `M${500 + 205 * Math.cos(a)},${350 + 100 * Math.sin(a)} L${500 + 396 * Math.cos(a)},${350 + 256 * Math.sin(a)}`; }), labels: [[500, 668, 'giù'], [645, 572, 'su']] }
};
const ROOMS = ['rettangolare', 'elle', 'rombo', 'quadrata', 'ovale', 'cerchio'];
const STAIRS = ['scala-dritta', 'scala-angoli', 'chiocciola', 'scala-ovale'];
const ROMAN = ['i.', 'ii.', 'iii.', 'iv.', 'v.', 'vi.'];
// Real recording pace: a slow pan (15° a second: a quarter turn in 6 s, half a turn in 12 s), a slow walk (0.5 m/s)
// and slower on stairs (0.35 m/s). Plans are drawn at about 140 units a metre (a 700-unit room ≈ 5 m).
const PACE = { turn: 15, walk: 0.5, stairs: 0.35 };
const PLAN_UNITS_PER_M = 140;
// Before starting, as in the guide: phone, lens, light; then the camera and microphone permission.
const ICONS = {
  phone: 'M8 2.5h8a1.5 1.5 0 0 1 1.5 1.5v16a1.5 1.5 0 0 1-1.5 1.5H8A1.5 1.5 0 0 1 6.5 20V4A1.5 1.5 0 0 1 8 2.5z M10.5 18.5h3',
  lens: 'M12 3a9 9 0 1 0 0 18a9 9 0 1 0 0-18z M12 8.5a3.5 3.5 0 1 0 0 7a3.5 3.5 0 1 0 0-7z',
  sun: 'M12 8a4 4 0 1 0 0 8a4 4 0 1 0 0-8z M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4'
};
const SETUP = [
  { t1: 'La casa,', t2: 'pronta',
    items: ['Telefono carico e «Non disturbare» attivo.', 'Telefono in verticale, all’altezza del petto.',
      'Tapparelle su e tende aperte: tutta la luce possibile.', 'Porte interne aperte.',
      'Tutto in ordine, come deve apparire. Poi non spostare più nulla.', 'Persone e animali fuori dagli spazi.'],
    primary: 'Sono pronto' }
];

function turnWords(g) { return g < 125 ? 'un quarto di giro' : g < 225 ? 'mezzo giro' : 'tre quarti di giro'; }
function doorInfo(key) {
  const [[x1, y1], [x2, y2]] = SHAPES[key].door, mx = (x1 + x2) / 2, my = (y1 + y2) / 2;
  let nx = -(y2 - y1), ny = x2 - x1; const L = Math.hypot(nx, ny); nx /= L; ny /= L;
  if ((500 - mx) * nx + (350 - my) * ny < 0) { nx = -nx; ny = -ny; }
  return { out: [mx - nx * 75, my - ny * 75], inn: [mx + nx * 110, my + ny * 110], dir: Math.atan2(ny, nx) * 180 / Math.PI };
}
const dirOf = (a, b) => Math.atan2(b[1] - a[1], b[0] - a[0]) * 180 / Math.PI;
function stepsOf(key) {
  const d = DATA[key], pts = d.punti, ar = d.frecce;
  const walk = (title, text, segs) => ({ kind: 'walk', title, text, segs, who: segs[0].da, look: dirOf(segs[0].da, segs[0].a) });
  if (ROOMS.includes(key)) {
    const di = doorInfo(key);
    const steps = [
      { kind: 'walk', title: 'Entra nella stanza', text: 'Mettiti fuori dalla porta. Premi Registra ed entra camminando piano, guardando avanti.', segs: [{ da: di.out, a: di.inn }], who: di.out, look: di.dir },
      { kind: 'walk', title: 'Esci dalla stanza', text: 'Mettiti dentro, davanti alla porta. Premi Registra ed esci camminando piano.', segs: [{ da: di.inn, a: di.out }], who: di.inn, look: di.dir + 180 }
    ];
    pts.forEach((p) => {
      const a = p.ampiezza || { da: 0, a: 359, gradi: 359 };
      steps.push({ kind: 'turn', title: `Punto ${p.n}`, text: `Vai al punto ${p.n}. Premi Registra e gira piano verso destra: ${turnWords(a.gradi)}, solo verso la stanza.`, point: p, arc: a, who: [p.x, p.y], look: a.da });
    });
    return steps;
  }
  if (key === 'corridoio') return [
    walk('Andata', 'Mettiti al punto 1 (Inizio del corridoio). Premi Registra e cammina piano fino al punto 2 (Fine del corridoio).', [ar[0]]),
    walk('Ritorno', 'Dal punto 2 (Fine del corridoio) premi Registra e torna al punto 1 (Inizio del corridoio), camminando in avanti.', [ar[1]])
  ];
  if (key === 'scala-dritta') return [
    walk('Sali', 'Una mano sul corrimano. Dal punto 1 premi Registra e sali piano fino al punto 2.', [ar[0]]),
    walk('Scendi', 'Dal punto 2 premi Registra e scendi piano fino al punto 1.', [ar[1]])
  ];
  if (key === 'scala-angoli') {
    const turn = (p) => ({ kind: 'turn', title: `Pianerottolo, punto ${p.n}`, text: `Al punto ${p.n} premi Registra e gira piano verso destra: ${turnWords(p.ampiezza.gradi)}.`, point: p, arc: p.ampiezza, who: [p.x, p.y], look: p.ampiezza.da });
    return [
      walk('Sali fino al pianerottolo', 'Una mano sul corrimano. Dal punto 1 premi Registra e sali piano fino al pianerottolo.', [ar[0]]),
      ...pts.filter((p) => p.ampiezza).map(turn),
      walk('Sali fino in cima', 'Dal punto 5 premi Registra e sali piano fino in cima.', [ar[1]]),
      walk('Torna giù', 'Dalla cima premi Registra e scendi piano fino al punto 1.', ar.slice(2))
    ];
  }
  if (d.ovale) {
    // Oval and spiral stairs: one arrow halfway between wall and well (or newel): up from point 1 to point 2, then the same way back down.
    const o = d.ovale, up = [];
    for (let g = o.da; g <= o.a + 0.01; g += 5) up.push([o.cx + o.rx * Math.cos(g * Math.PI / 180), o.cy + o.ry * Math.sin(g * Math.PI / 180)]);
    const down = up.slice().reverse();
    const curve = (title, text, c) => ({ kind: 'walk', title, text, curve: c, segs: [], who: c[0], look: dirOf(c[0], c[1]) });
    return [
      curve('Sali', 'Una mano sul corrimano. Dal punto 1 premi Registra e sali piano seguendo la freccia fino al punto 2.', up),
      curve('Scendi', 'Dal punto 2 premi Registra e scendi piano seguendo la freccia, fino al punto 1.', down)
    ];
  }
  return [walk('Sali girando', 'Una mano sul corrimano. Dal punto 1 premi Registra e sali piano seguendo le frecce, passando per tutti i punti.', ar)];
}
function splitTitle(t) { const i = t.lastIndexOf(' '); return i < 0 ? ['', t] : [t.slice(0, i), t.slice(i + 1)]; }

// The plan as path strings (viewBox 1000×700) plus point numbers and labels placed over it in percent.
function planOf(key, step) {
  const s = SHAPES[key], d = DATA[key], f = (n) => Math.round(n * 10) / 10;
  const circ = (x, y, r) => `M${f(x - r)},${f(y)} a${r},${r} 0 1,0 ${2 * r},0 a${r},${r} 0 1,0 ${-2 * r},0 Z`;
  const ell = (e) => `M${e[0] - e[2]},${e[1]} a${e[2]},${e[3]} 0 1,0 ${2 * e[2]},0 a${e[2]},${e[3]} 0 1,0 ${-2 * e[2]},0 Z`;
  const head = (x, y, ux, uy) => `M${f(x)},${f(y)} L${f(x - ux * 34 - uy * 18)},${f(y - uy * 34 + ux * 18)} L${f(x - ux * 34 + uy * 18)},${f(y - uy * 34 - ux * 18)} Z`;
  const pct = (x, y) => ({ x: (x / 10) + '%', y: (y / 7) + '%' });
  const P = {
    label: step ? `Pianta: ${step.title}` : `Pianta ${s.name}`,
    walls: (s.walls || []).join(' ') + (s.ellipse ? ' ' + ell(s.ellipse) : ''),
    fill: step && (ROOMS.includes(key) || key === 'corridoio') ? (s.walls || []).join(' ') + (s.ellipse ? ' ' + ell(s.ellipse) : '') : '',
    bgd: step ? '' : 'M36,0 H964 A36,36 0 0 1 1000,36 V664 A36,36 0 0 1 964,700 H36 A36,36 0 0 1 0,664 V36 A36,36 0 0 1 36,0 Z',
    inner: s.inner ? ell(s.inner) : '', newel: s.newel ? circ(s.newel[0], s.newel[1], s.newel[2]) : '',
    stairs: s.steps ? s.steps().join(' ') : '',
    door: s.door ? `M${s.door[0][0]},${s.door[0][1]} L${s.door[1][0]},${s.door[1][1]}` : '',
    icon: '', others: '', cone: '', arc: '', arcHead: '', segs: '', heads: '', person: '', tick: '', nums: [],
    tx: 0, ty: 0, rf: '0deg', rt: '0deg', rdur: '6s', turnDisp: 'none', route: 'M0,0', wdur: '4s', walkDisp: 'none', wait: '0ms',
    show: '0ms', dstep: '50ms', dz: {},
    labels: (s.labels || []).map(([x, y, t]) => Object.assign(pct(x, y), { t }))
  };
  if (!step) { P.icon = d.punti.map((p) => circ(p.x, p.y, 22)).join(' '); return P; }
  d.punti.forEach((p) => {
    const cur = step.point && step.point.n === p.n, done = step.point && p.n < step.point.n;
    P.nums.push(Object.assign(pct(p.x, p.y), { n: p.n, i: P.nums.length + 1, st: cur ? 'cur' : done ? 'done' : 'todo' }));
  });
  // Timing: the points pop in from 1350ms, 110ms apart. Cone and arrow come right after the point to record from
  // (for the door steps, after all of them); the move starts once every point and every dash is there.
  const allIn = 1350 + P.nums.length * 110 + 420;
  const from = step.point || d.punti.find((p) => Math.hypot(p.x - step.who[0], p.y - step.who[1]) < 60);
  const at = from ? d.punti.findIndex((p) => p.n === from.n) + 1 : 0;
  const show = at ? 1350 + at * 110 + 420 : allIn;
  const DASH = 12, GAP = 14, dz = [];
  const line = (x1, y1, x2, y2) => {
    const L = Math.hypot(x2 - x1, y2 - y1) || 1, ux = (x2 - x1) / L, uy = (y2 - y1) / L;
    for (let u = 0; u < L; u += DASH + GAP) { const v = Math.min(u + DASH, L); dz.push(`M${f(x1 + ux * u)},${f(y1 + uy * u)} L${f(x1 + ux * v)},${f(y1 + uy * v)}`); }
  };
  const [wx, wy] = step.who;
  if (step.kind === 'turn') {
    const a = step.arc, R = 130, flag = a.verso === 'antiorario' ? 0 : 1, large = a.gradi > 180 ? 1 : 0;
    const x0 = wx + R * Math.cos(rad(a.da)), y0 = wy + R * Math.sin(rad(a.da)), x1 = wx + R * Math.cos(rad(a.a)), y1 = wy + R * Math.sin(rad(a.a));
    P.tx = wx; P.ty = wy; P.turnDisp = 'inline';
    P.rf = a.da + 'deg'; P.rt = (a.da + (flag ? a.gradi : -a.gradi)) + 'deg';
    P.rdur = (a.gradi / PACE.turn / 0.84).toFixed(1) + 's';
    const sg = flag ? 1 : -1, t = rad(a.a), deg = 180 / Math.PI;
    const pol = (g) => `${f(wx + R * Math.cos(rad(g)))},${f(wy + R * Math.sin(rad(g)))}`;
    const total = a.gradi - 30 / R * deg, dd = DASH / R * deg, pd = (DASH + GAP) / R * deg;
    for (let u = 0; u < total; u += pd) dz.push(`M${pol(a.da + sg * u)} A${R},${R} 0 0,${flag} ${pol(a.da + sg * Math.min(u + dd, total))}`);
    dz.push(head(x1, y1, -Math.sin(t) * sg, Math.cos(t) * sg));
  } else {
    if (step.curve) {
      // A curved arrow: dashes measured along the whole line, trimmed at both ends like the straight ones, one head.
      const c = step.curve, cum = [0];
      for (let k = 1; k < c.length; k++) cum.push(cum[k - 1] + Math.hypot(c[k][0] - c[k - 1][0], c[k][1] - c[k - 1][1]));
      const L = cum[cum.length - 1], end = L - 30;
      const at = (u) => { let k = 1; while (k < c.length - 1 && cum[k] < u) k++; const t = (u - cum[k - 1]) / ((cum[k] - cum[k - 1]) || 1); return [c[k - 1][0] + (c[k][0] - c[k - 1][0]) * t, c[k - 1][1] + (c[k][1] - c[k - 1][1]) * t]; };
      for (let u = 28; u < end; u += DASH + GAP) {
        const v = Math.min(u + DASH, end), q = [at(u)];
        cum.forEach((m, k) => { if (m > u && m < v) q.push(c[k]); });
        q.push(at(v));
        dz.push('M' + q.map((r) => `${f(r[0])},${f(r[1])}`).join(' L'));
      }
      const [ax, ay] = c[c.length - 2], [bx, by] = c[c.length - 1], hl = Math.hypot(bx - ax, by - ay) || 1;
      dz.push(head(bx, by, (bx - ax) / hl, (by - ay) / hl));
    }
    step.segs.forEach((sgm) => {
      const [x1, y1] = sgm.da, [x2, y2] = sgm.a, L = Math.hypot(x2 - x1, y2 - y1) || 1, ux = (x2 - x1) / L, uy = (y2 - y1) / L;
      line(x1 + ux * 28, y1 + uy * 28, x2 - ux * 30, y2 - uy * 30);
      dz.push(head(x2, y2, ux, uy));
    });
    const R = 150, hw = 32, x0 = wx + R * Math.cos(rad(step.look - hw)), y0 = wy + R * Math.sin(rad(step.look - hw)), x1 = wx + R * Math.cos(rad(step.look + hw)), y1 = wy + R * Math.sin(rad(step.look + hw));
    P.cone = `M${wx},${wy} L${f(x0)},${f(y0)} A${R},${R} 0 0,1 ${f(x1)},${f(y1)} Z`;
  }
  const dstep = Math.min(70, Math.max(20, 2400 / dz.length));
  dz.forEach((q, k) => { P.dz['d' + k] = q; });
  P.show = show + 'ms'; P.dstep = dstep.toFixed(1) + 'ms';
  P.wait = Math.round(Math.max(allIn, show + dz.length * dstep + 250)) + 'ms';
  P.nDash = dz.length;  // 72 dash slots in plan_html; the longest arrow today (oval stair) has about 55
  if (step.kind === 'turn') return P;  // the white point already marks where to stand
  // walking: one route through all the arrows, at a slow walking pace (slower on stairs)
  const pts = step.curve ? step.curve.slice() : [];
  step.segs.forEach((sgm) => { pts.push(sgm.da, sgm.a); });
  P.route = 'M' + pts.map((q) => `${f(q[0])},${f(q[1])}`).join(' L');
  let len = 0;
  for (let k = 1; k < pts.length; k++) len += Math.hypot(pts[k][0] - pts[k - 1][0], pts[k][1] - pts[k - 1][1]);
  P.wdur = (len / PLAN_UNITS_PER_M / (STAIRS.includes(key) ? PACE.stairs : PACE.walk) / 0.84).toFixed(1) + 's';
  P.walkDisp = 'inline';
  P.cone = '';
  return P;
}
const BLANK = planOf('rettangolare');

// ---- First person: from the phone's spot, a ray every degree finds the nearest wall; its distance sets where
// ceiling and floor meet the wall (camera 1.5 m up, ceiling 2.7 m, door 2.1 m), seen wide like the 0.5× lens (8 px a degree,
// about 125° across) and squeezed in height so floor and ceiling stay in the frame.
function wallsOf(key) {
  const s = SHAPES[key], segs = [], ells = [];
  (s.walls || []).forEach((w) => {
    let x = 0, y = 0, sx = 0, sy = 0;
    const t = w.match(/[MLHVZ]|-?[\d.]+/g);
    for (let i = 0; i < t.length;) {
      const c = t[i++];
      const nx = c === 'H' ? +t[i++] : c === 'V' ? x : c === 'Z' ? sx : +t[i++];
      const ny = c === 'H' ? y : c === 'V' ? +t[i++] : c === 'Z' ? sy : +t[i++];
      if (c === 'M') { sx = nx; sy = ny; } else segs.push([x, y, nx, ny]);
      x = nx; y = ny;
    }
  });
  if (s.ellipse) ells.push(s.ellipse);
  if (s.inner) ells.push(s.inner);
  if (s.newel) ells.push([s.newel[0], s.newel[1], s.newel[2], s.newel[2]]);
  return { segs, ells, door: s.door };
}
function castRay(W, ox, oy, deg) {
  const dx = Math.cos(rad(deg)), dy = Math.sin(rad(deg));
  let best = 1e9, id = -1;
  // the doorway is an opening: a hit on it does not stop the ray
  const inDoor = (t) => {
    if (!W.door) return false;
    const [[ax, ay], [bx, by]] = W.door, hx = ox + dx * t, hy = oy + dy * t, ex = bx - ax, ey = by - ay, L2 = ex * ex + ey * ey;
    const u = Math.max(0, Math.min(1, ((hx - ax) * ex + (hy - ay) * ey) / L2));
    return Math.hypot(hx - ax - ex * u, hy - ay - ey * u) < 14 && u > 0.02 && u < 0.98;
  };
  W.segs.forEach(([x1, y1, x2, y2], k) => {
    const ex = x2 - x1, ey = y2 - y1, den = dx * ey - dy * ex;
    if (Math.abs(den) < 1e-9) return;
    const t = ((x1 - ox) * ey - (y1 - oy) * ex) / den, u = ((x1 - ox) * dy - (y1 - oy) * dx) / den;
    if (t > 1 && u >= 0 && u <= 1 && t < best && !inDoor(t)) { best = t; id = k; }
  });
  W.ells.forEach(([cx, cy, rx, ry], k) => {
    const px = (ox - cx) / rx, py = (oy - cy) / ry, qx = dx / rx, qy = dy / ry;
    const A = qx * qx + qy * qy, B = 2 * (px * qx + py * qy), C = px * px + py * py - 1, D = B * B - 4 * A * C;
    if (D < 0) return;
    [(-B - Math.sqrt(D)) / (2 * A), (-B + Math.sqrt(D)) / (2 * A)].forEach((t) => { if (t > 1 && t < best && !inDoor(t)) { best = t; id = 100 + k; } });
  });
  return { d: Math.min(best, 1600), id: best > 1600 ? -1 : id };
}
function fpOf(key, step) {
  const s = SHAPES[key], W = wallsOf(key), f = (n) => Math.round(n * 10) / 10, PX = 8, FC = PX * 180 / Math.PI, FV = FC * 0.5;
  const turn = step.kind === 'turn', [ox, oy] = step.who;
  const look = turn ? step.arc.da : step.look, span = turn ? step.arc.gradi : 0;
  const yC = (d) => 350 - FV * 168 / d, yF = (d) => 350 + FV * 210 / d, yD = (d) => 350 - FV * 84 / d;
  const g0 = look - 70, g1 = look + span + 70, X = (g) => 500 + (g - look) * PX;
  let lines = '', fine = '', door = '', ceil = [], flr = [], prev = null;
  const flush = () => {
    if (ceil.length > 1) {
      lines += 'M' + ceil.map((q) => q.join(',')).join(' L') + ' M' + flr.map((q) => q.join(',')).join(' L') + ' ';
    }
    ceil = []; flr = [];
  };
  const wallPoly = [], floorPoly = [];
  for (let g = g0; g <= g1 + 0.01; g += 1) {
    const r = castRay(W, ox, oy, g), x = f(X(g));
    if (r.id < 0) { if (prev && prev.id >= 0) flush(); prev = r; continue; }
    const c = f(Math.max(-40, yC(r.d))), fl = f(Math.min(740, yF(r.d)));
    // a corner, or a nearer wall hiding a farther one: a vertical line where the wall changes
    if (prev && prev.id >= 0 && prev.id !== r.id) {
      const dn = Math.min(prev.d, r.d), jump = Math.abs(prev.d - r.d) / dn > 0.12;
      if (jump) flush();
      lines += `M${x},${f(Math.max(-40, yC(dn)))} L${x},${f(Math.min(740, yF(dn)))} `;
    }
    ceil.push([x, c]); flr.push([x, fl]);
    wallPoly.push([x, c, fl]);
    prev = r;
  }
  flush();
  const wall = wallPoly.length ? 'M' + wallPoly.map((q) => `${q[0]},${q[1]}`).join(' L') + ' L' + wallPoly.slice().reverse().map((q) => `${q[0]},${q[2]}`).join(' L') + ' Z' : '';
  const floor = wallPoly.length ? 'M' + wallPoly.map((q) => `${q[0]},${q[2]}`).join(' L') + ` L${wallPoly[wallPoly.length - 1][0]},760 L${wallPoly[0][0]},760 Z` : '';
  // the door: its two edges, if not hidden, from floor to 2.1 m, and the lintel
  if (s.door) {
    const ends = s.door.map(([x, y]) => {
      let g = Math.atan2(y - oy, x - ox) * 180 / Math.PI;
      while (g < g0) g += 360; while (g > g1) g -= 360;
      const d = Math.hypot(x - ox, y - oy), r = castRay(W, ox, oy, g);
      return { g, d, ok: g >= g0 && g <= g1 && r.d > d - 25 };  // r passes the opening, so it ends at or beyond the edge
    });
    if (ends[0].ok && ends[1].ok) {
      const [a, b] = ends;
      door = `M${f(X(a.g))},${f(yF(a.d))} L${f(X(a.g))},${f(yD(a.d))} L${f(X(b.g))},${f(yD(b.d))} L${f(X(b.g))},${f(yF(b.d))}`;
    }
  }
  // stairs: treads ahead, every 28 cm, across the floor between the walls
  if (STAIRS.includes(key) && !turn) {
    const ahead = castRay(W, ox, oy, look).d;  // on curved stairs the treads stop at the wall straight ahead
    for (let k = 1; k < 18; k++) {
      const d = 60 + k * 39, y = f(yF(d) - k * 3);
      if (y < 352 || d > ahead - 20) break;
      fine += `M${f(500 - FC * 95 / d)},${y} L${f(500 + FC * 95 / d)},${y} `;
    }
  }
  // walking: how much closer the wall straight ahead comes over the walk
  let zoom = 1;
  if (!turn) {
    const pts = step.curve || step.segs.flatMap((sg) => [sg.da, sg.a]);
    let len = 0; for (let k = 1; k < pts.length; k++) len += Math.hypot(pts[k][0] - pts[k - 1][0], pts[k][1] - pts[k - 1][1]);
    const ahead = castRay(W, ox, oy, look).d;
    zoom = step.curve ? 1.5 : Math.min(2.6, ahead / Math.max(ahead - len, ahead * 0.38));
  }
  return {
    lines, fine, door, wall, floor, mode: turn ? 'fp-turn' : 'fp-walk',
    sx: (-span * PX) + 'px', zoom: zoom.toFixed(2),
    label: turn ? `Vista in prima persona: giri piano verso destra, ${turnWords(span)}` : 'Vista in prima persona: cammini piano in avanti'
  };
}


"""

FLOW_METHODS = r"""  // ---- Navigation: one artboard holds the whole flow; history works like the prototype's back button. ----
  cur() { return (this.state && this.state.scr) || { type: 'setup', i: 0 }; }
  hist() { return ((this.state && this.state.hist) || []).slice(); }
  go(screen, push) {
    const c = this.cur(), h = this.hist();
    if (push !== false && c.type !== 'rec') h.push(c);
    this.enter(screen, h);
  }
  // A new screen: reset the motion for a frame so its pieces set down again; the music hushes while recording.
  enter(screen, h) {
    const wasRec = this.cur().type === 'rec';
    this.setState({ scr: screen, hist: h, replay: true });
    clearTimeout(this._replay);
    this._replay = setTimeout(() => this.setState({ replay: false }), 40);
    if (screen.type === 'rec' && this.musicOn()) this.fadeTo(0, true);
    if (wasRec && screen.type !== 'rec' && this.musicOn()) this.startMusic(this.shared().time);
  }
  goBack() {
    const h = this.hist();
    if (!h.length) return;
    this.enter(h.pop(), h);
  }
  nextStep(sc) {
    const n = stepsOf(sc.key).length;
    if (sc.i + 1 < n) this.go({ type: 'step', key: sc.key, i: sc.i + 1 });
    else this.enter({ type: 'space', fatto: sc.key, last: sc.i }, []);
  }
  // After a take (or a skipped point) the camera stays on and shows the next step, ready: one tap to record it.
  // The history stays the one of the step screens, so Pianta and Indietro work as before.
  afterRec(sc, recorded) {
    const n = stepsOf(sc.key).length, h = this.hist().concat([{ type: 'step', key: sc.key, i: sc.i }]);
    if (sc.i + 1 < n) this.enter({ type: 'rec', key: sc.key, i: sc.i + 1, ready: true, guide: true, prev: recorded ? sc.i : null }, h);
    else this.enter({ type: 'space', fatto: sc.key, last: sc.i }, []);   // the space is done: straight to the next one (its last take can be done again from there)
  }
  // The permission screen: in the canvas it only moves on; the guide asks the phone for camera and microphone here.
  allowCamera() { this.go({ type: 'space' }); }
  // Feedback: kept in state for the prototype; where it is sent is decided with the real guide.
  feedbackVals() {
    const st = this.state || {}, fb = st.fb || {}, max = Math.max(20, Math.round(this.props.feedbackMax ?? 300));
    const rating = fb.rating || 0, text = (fb.text || '').slice(0, max), left = max - text.length;
    const WORDS = ['Tocca una stella', 'Da migliorare', 'Così così', 'Buona', 'Molto buona', 'Ottima'];
    const set = (o) => this.setState({ fb: Object.assign({}, fb, o) });
    return {
      isOpen: !!fb.open, form: !!fb.open && !fb.sent, sent: !!fb.sent,
      // once sent, the button in the header says thank you (it still opens the sheet for another note)
      ask: !(fb.sent || fb.done), thanked: !!(fb.sent || fb.done),
      open: () => this.setState({ fb: { open: true, rating: 0, text: '', done: !!(fb.sent || fb.done) } }),
      close: () => this.setState({ fb: { open: false, done: !!(fb.sent || fb.done) } }),
      stars: [1, 2, 3, 4, 5].map((n) => ({
        fill: n <= rating ? '#D9C29A' : 'none', checked: n === rating ? 'true' : 'false',
        label: n === 1 ? '1 stella' : n + ' stelle', pick: () => set({ rating: n })
      })),
      word: WORDS[rating], max, text, type: (e) => set({ text: String(e.target.value).slice(0, max) }),
      count: `${text.length} / ${max}`, countColor: left <= 20 ? '#E6D3B0' : 'rgba(243,235,221,.7)',
      cannot: !rating, sendOpacity: rating ? 1 : 0.5,
      send: () => { if (rating) set({ sent: true, sentAt: Date.now() }); }
    };
  }
  // Glass pieces come and go with the screens: measure them again after every change (no-op when nothing moved).
  componentDidUpdate() { this.measure(); }
  flowVals() {
    const sc = this.cur(), h = this.hist();
    const v = {
      isSetup: sc.type === 'setup', isPerm: sc.type === 'perm', isSpace: sc.type === 'space', isPick: sc.type === 'pick', isStep: sc.type === 'step',
      isRec: sc.type === 'rec', isDone: sc.type === 'done', isEnd: sc.type === 'end',
      // setup, permission and step screens have Indietro at the bottom, as in the guide; the others a chevron at the top
      hasBack: h.length > 0 && !['step', 'setup', 'perm'].includes(sc.type), noBack: h.length === 0 || ['step', 'setup', 'perm'].includes(sc.type), goBack: () => this.goBack(),
      snd: this.glass('snd'), fig: this.glass('fig'), back: this.glass('back'), fb: this.feedbackVals(),
      setup: { items: [], segs: [] }, perm: {}, pick: { tiles: [], go: {} }, step: { plan: BLANK, fp: {}, segs: [], actions: [] }, rec: { plan: BLANK },
      space: {
        ambiente: () => this.go({ type: 'rec', key: 'rettangolare', i: 0, ready: true, guide: true }), corridoio: () => this.go({ type: 'rec', key: 'corridoio', i: 0, ready: true, guide: true }),
        scala: () => this.go({ type: 'pick', group: 'stairs' }), finish: () => this.go({ type: 'end' }),
        crumb: sc.fatto ? 'Spazio finito · scegli il prossimo' : 'Scegli lo spazio',
        hasRedo: !!sc.fatto && sc.last != null, redoLabel: sc.fatto && sc.last != null ? 'Rifai «' + stepsOf(sc.fatto)[sc.last].title + '»' : '',
        redo: () => this.enter({ type: 'rec', key: sc.fatto, i: sc.last, ready: true, guide: true }, [{ type: 'space' }])
      },
      done: { another: () => this.enter({ type: 'space' }, []), finish: () => this.go({ type: 'end' }) },
      end: { restart: () => this.enter({ type: 'setup', i: 0 }, []) }
    };
    if (sc.type === 'setup') {
      const si = Math.min(sc.i, SETUP.length - 1), s = SETUP[si], many = SETUP.length > 1;
      v.setup = Object.assign({}, s, { items: s.items.map((t, i) => ({ n: ROMAN[i], t })), passo: many ? `${si + 1} / ${SETUP.length}` : '', hasBack: si > 0, noKicker: !s.kicker,
        noteTop: !!(s.note && s.noteTop), noteBottom: !!(s.note && !s.noteTop),
        segs: many ? SETUP.map((_, k) => ({ cls: k === si ? 'seg-new' : '', bg: k <= si ? '#D9C29A' : 'rgba(243,235,221,.3)' })) : [],
        next: () => this.go(si < SETUP.length - 1 ? { type: 'setup', i: si + 1 } : { type: 'perm' }) });
    }
    if (sc.type === 'perm') {
      // In the canvas this only moves on; the working prototype asks the phone for camera and microphone here.
      v.perm = { allow: () => this.allowCamera() };
    }
    if (sc.type === 'pick') {
      const rooms = sc.group === 'rooms', keys = rooms ? ROOMS : STAIRS;
      const go = {};
      // Holes can't read a hyphen, so 'scala-dritta' is reached as go.scala_dritta.
      ROOMS.concat(STAIRS).forEach((k) => { go[k.replace('-', '_')] = () => this.go({ type: 'rec', key: k, i: 0, ready: true, guide: true }); });
      v.pick = { rooms, stairs: !rooms, go, crumb: rooms ? 'Ambiente' : 'Scalinata', t1: rooms ? 'Che forma' : 'Che scala', t2: rooms ? 'ha?' : 'è?',
        tiles: keys.map((k, i) => ({ name: SHAPES[k].name, plan: planOf(k), d: (450 + i * 60) + 'ms', s: i === 0 ? '3' : '',
          pick: () => this.go({ type: 'rec', key: k, i: 0, ready: true, guide: true }) })) };
    }
    if (sc.type === 'step') {
      const steps = stepsOf(sc.key), st = steps[sc.i], [t1, t2] = splitTitle(st.title);
      const area = ROOMS.includes(sc.key) ? 'Ambiente · ' + SHAPES[sc.key].name : STAIRS.includes(sc.key) ? 'Scalinata · ' + SHAPES[sc.key].name : 'Corridoio';
      const segs = steps.map((_, k) => ({ cls: k === sc.i ? 'seg-new' : '', bg: k <= sc.i ? '#D9C29A' : 'rgba(243,235,221,.3)' }));
      const actions = st.text.split(/(?<=\.)\s+/).filter(Boolean).map((t, k) => ({ n: ROMAN[k], t, d: (500 + k * 45) + 'ms' }));
      const kicker = st.kind === 'turn' ? 'Gira verso destra · ' + turnWords(st.arc.gradi) : 'Cammina piano, telefono avanti';
      const fpOn = !!(this.state && this.state.fpView);
      v.step = { fp: fpOf(sc.key, st), view: fpOn ? 'v-fp' : 'v-plan', planOn: fpOn ? 'false' : 'true', fpOn: fpOn ? 'true' : 'false',
        showPlan: () => this.setState({ fpView: false }), showFp: () => this.setState({ fpView: true }),
        area, passo: `${sc.i + 1} / ${steps.length}`, n: steps.length, segs, actions, kicker, t1, t2, text: st.text, plan: planOf(sc.key, st), isTurn: st.kind === 'turn',
        skip: () => this.nextStep(sc), rec: () => this.enter({ type: 'rec', key: sc.key, i: sc.i, guide: true }, this.hist()) };
    }
    if (sc.type === 'rec') {
      const steps = stepsOf(sc.key), st = steps[sc.i], ready = !!sc.ready, prev = ready && sc.prev != null ? steps[sc.prev] : null;
      const rp = planOf(sc.key, st), turn = st.kind === 'turn';
      const AVV = { Automatico: 'auto', Nessuno: 'none', 'Più piano': 'piano', 'Tieni dritto': 'dritto', 'Poca luce': 'luce' };
      v.rec = { plan: rp, guide: !!sc.guide, noGuide: !sc.guide, isTurn: turn, isWalk: !turn,
        turnWords: turn ? turnWords(st.arc.gradi) : '', turnLabel: turn ? 'Gira a destra, ' + turnWords(st.arc.gradi) : '',
        rdur: rp.rdur, wdur: rp.wdur, deg: (turn ? st.arc.gradi : 0) + 'deg',
        dashEnd: (553 * (1 - (turn ? st.arc.gradi : 0) / 360)).toFixed(1),
        avv: AVV[this.props.avviso] || 'auto',
        text: ready ? st.text : st.title + ': ' + (st.kind === 'turn' ? `gira verso destra, ${turnWords(st.arc.gradi)}.` : 'cammina piano, guardando avanti.'),
        passo: (sc.key === 'corridoio' ? '' : SHAPES[sc.key].name + ' · ') + `passo ${sc.i + 1} di ${steps.length}`,
        canShape: ready && sc.i === 0 && ROOMS.includes(sc.key), shape: () => this.go({ type: 'pick', group: 'rooms' }),
        trailText: turn ? 'Segui la freccia · ' + turnWords(st.arc.gradi) : '', aimLen: (turn ? st.arc.gradi * 6 : 0) + 'px',
        ready, live: !ready, mode: ready ? 'is-ready' : 'is-live', clock: (this.state && this.state.clock) || '0:00',
        hasNote: ready && !!sc.note, note: sc.note || '', canSkip: ready && turn,
        hasRedo: !!prev, redoLabel: prev ? 'Rifai «' + prev.title + '»' : '',
        hide: () => this.setState({ scr: Object.assign({}, sc, { guide: false }) }),
        show: () => this.setState({ scr: Object.assign({}, sc, { guide: true }) }),
        start: () => this.enter({ type: 'rec', key: sc.key, i: sc.i, guide: true }, this.hist()),
        stop: () => this.afterRec(sc, true),
        skip: () => this.afterRec(sc, false),
        toPlan: () => this.enter({ type: 'step', key: sc.key, i: sc.i }, this.hist()),
        redo: () => this.enter({ type: 'rec', key: sc.key, i: sc.prev, ready: true, guide: true }, this.hist().slice(0, -1)) };
    }
    return v;
  }
"""

script = b.SCRIPT.replace("e.animationName === 'posa' && e.target.dataset",
                          "(e.animationName === 'posa' || e.animationName === 'posa-free') && e.target.dataset")
# Every tap on a button gets a soft "tchk"; not the speaker (it has its own logic) and not while recording (microphone on).
script = script.replace("""        // Each of the 8 points of the plan pops as it appears.""",
"""        click: (e) => {
          const t = e.target && e.target.closest ? e.target.closest('button, [role="button"], a') : null;
          if (t && !t.closest('.snd') && !t.closest('.rec-screen')) this.tchk();
        },
        // Each of the 8 points of the plan pops as it appears.""")
script = script.replace("""  // One knock: a sharp contact click""",
"""  // A tap: a soft, short "tchk" (a breath of filtered noise, then a small muted click with a hint of body).
  tchk() {
    const c = this.ctx();
    if (!c || !this.musicOn()) return;
    if (c.state !== 'running') { c.resume(); return; }
    const t = c.currentTime + 0.005, out = c.createGain();
    out.gain.value = 0.2;
    out.connect(c.destination);
    this.noise(c, out, t, 0.022, 'bandpass', 2600, 0.45);
    [[1250, 0.35, 0.018], [210, 0.6, 0.05]].forEach(([fr, a, dcy]) => {
      const o = c.createOscillator(), g = c.createGain();
      o.type = 'sine';
      o.frequency.setValueAtTime(fr * 1.1, t + 0.012);
      o.frequency.exponentialRampToValueAtTime(fr, t + 0.03);
      g.gain.setValueAtTime(0.0001, t + 0.012);
      g.gain.exponentialRampToValueAtTime(a, t + 0.014);
      g.gain.exponentialRampToValueAtTime(0.0001, t + 0.012 + dcy);
      o.connect(g).connect(out);
      o.start(t + 0.012);
      o.stop(t + 0.08);
    });
  }
  // One knock: a sharp contact click""")
assert "tchk()" in script and "this.tchk()" in script
# The transition knocks keep their tun-tun-ta-ta pitches but take the calm of the tchk: a breath of noise first,
# a softer attack with a small settling glide, fewer bright partials, a short muted body underneath.
_k_old = "    this.wood(c, out, c.currentTime + 0.005, k[0], k[1], k[2]);"
assert script.count(_k_old) == 1
script = script.replace(_k_old, "    this.softWood(c, out, c.currentTime + 0.005, k[0], k[1], k[2]);")
script = script.replace("""  // One knock: a sharp contact click""", """  // A knock between wood and tchk: the wood pitch, struck softly and damped sooner.
  softWood(c, out, t, f, decay, level) {
    this.noise(c, out, t, 0.02, 'bandpass', 2400, 0.32 * level);
    const s = t + 0.008;
    [[f, 0.85, decay * 0.8], [f * 2.76, 0.14, decay * 0.35], [f * 0.42, 0.4, 0.05]].forEach(([fr, a, d]) => {
      const o = c.createOscillator(), g = c.createGain();
      o.type = 'sine';
      o.frequency.setValueAtTime(fr * 1.06, s);
      o.frequency.exponentialRampToValueAtTime(fr, s + 0.025);
      g.gain.setValueAtTime(0.0001, s);
      g.gain.exponentialRampToValueAtTime(a * level, s + 0.005);
      g.gain.exponentialRampToValueAtTime(0.0001, s + d);
      o.connect(g).connect(out);
      o.start(s);
      o.stop(s + d + 0.05);
    });
  }
  // One knock: a sharp contact click""", 1)
assert "this.softWood(" in script and "  softWood(c, out" in script
script = script.replace("class Component extends DCLogic {", FLOW_JS.replace("__DATA__", json.dumps(DATA, ensure_ascii=False)) + "class Component extends DCLogic {")
script = script.replace("  // Each glass piece shows the meadow", FLOW_METHODS + "  // Each glass piece shows the meadow")

LENS_FILTERS = b.filters({"snd": "round", "fig": "card", "back": "pill"})
css = "\n".join([b.HEAD_CSS, b.SND_CSS, b.PILL_CSS, b.MOTION_CSS, EXTRA_CSS])
html = f'''<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<title>Prototipo guida riprese</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,300..700&amp;family=Bodoni+Moda:ital,opsz,wght@0,6..96,400..700;1,6..96,400..700&amp;family=GFS+Didot&amp;display=swap">
<style>
{css}
</style>
</helmet>
<div ref="{{{{ rootRef }}}}" class="prato {{{{animClass}}}}" style="position: relative; width: 390px; height: 844px; overflow: hidden; color: #F3EBDD; font-family: Archivo, system-ui, sans-serif; --display: {{{{displayFont}}}}">
  <svg aria-hidden="true" width="0" height="0" style="position: absolute">
{LENS_FILTERS}
  </svg>
  <video class="prato-video" src="/_blob/a78189329319cf3af17d4e9383c05b28" autoplay="autoplay" muted="muted" loop="loop" playsinline="playsinline" preload="auto" aria-hidden="true"></video>
  <div aria-hidden="true" style="position: absolute; inset: 0; background: {{{{veilBg}}}}"></div>
{BODY}
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"display":{{"editor":"enum","options":["Bodoni Moda","GFS Didot"],"default":"Bodoni Moda","section":"Tipografia"}},"veil":{{"editor":"range","min":0.2,"max":0.8,"step":0.05,"default":0.45,"section":"Leggibilità"}},"animazioni":{{"editor":"boolean","default":true,"section":"Movimento"}},"feedbackMax":{{"editor":"int","min":50,"max":1000,"step":10,"default":300,"section":"Feedback"}},"avviso":{{"editor":"enum","options":["Automatico","Nessuno","Più piano","Tieni dritto","Poca luce"],"default":"Automatico","section":"Registrazione"}},"$preview":{{"width":390,"height":844}}}}'>
{script}  renderVals() {{
    const display = this.props.display ?? 'Bodoni Moda';
    const v = this.props.veil ?? 0.45;
    const a = (x) => Math.max(0, Math.min(0.96, x)).toFixed(2);
    return Object.assign(this.flowVals(), {{
      rootRef: (el) => {{ this._root = el; }},
      animClass: this.state && this.state.replay ? 'prep' : ((this.props.animazioni ?? true) ? 'anim' : ''),
      music: this.musicOn(), musicOff: !this.musicOn(),
      musicPressed: String(this.musicOn()),
      musicLabel: this.musicOn() ? 'Spegni la musica' : 'Accendi la musica',
      toggleMusic: () => this.toggleMusic(),
      displayFont: '"' + display + '", "Bodoni Moda", Didot, serif',
      veilBg: 'linear-gradient(180deg, rgba(18,15,9,' + a(v) + ') 0%, rgba(18,15,9,.16) 28%, rgba(18,15,9,.16) 68%, rgba(18,15,9,' + a(v + 0.1) + ') 100%)'
    }});
  }}
}}
</script>
</body>
</html>
'''
for old, new in BLOBS.items():
    html = html.replace(old, new)
open(OUT + "/Main.dc.html", "w", encoding="utf-8").write(html)
print("written", len(html))
