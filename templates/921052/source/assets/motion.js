/* ============================================================
   Motion.mini v1.2 — 逐帧可寻址时间线（无第三方依赖）
   为什么自己写：模板要能在任意帧独立渲染（seek-safe）、离线、
   无第三方许可负担；对这类固定关键帧动效，一个确定性时间线足够，
   渲染结果与预览完全一致。

   API
   ----
   const tl = Motion.timeline();
   tl.fromTo(target, {opacity:0, y:40}, {opacity:1, y:0, duration:0.6, ease:"power3.out", at:0.4});
   tl.to(target, {opacity:0.8, duration:0.8, ease:"power2.out", at:1.2});
   tl.set(target, {display:"none"}, 5.0);
   tl.seek(seconds);          // 任意时刻重算全部属性，双向安全
   tl.duration;               // 自动推导

   同一元素同一属性可以先后有多条 tween：
   - 第一条开始前 → 显示第一条的 from；
   - 两条之间 → 保持前一条的结束值；
   - 区间内 → 插值。
   因此 "先 fromTo 入场、再 to 做收尾" 不会把前段压成 0。

   支持的 ease：linear / none / power1.out…power4.out /
   power1.inOut…power4.inOut / sine.out / sine.inOut / back.out
   动画属性：opacity, x, y, scale, scaleX, scaleY, rotation，
   以及数值型 CSS 属性（fontSize 等）；也可传 function(k) 计算值。
   transform 元素不要同时在 CSS 里写 transform，否则会被本引擎覆盖。
   ============================================================ */
(function (global) {
  "use strict";

  var EASES = {
    none: function (t) { return t; },
    linear: function (t) { return t; },
    "power1.out": function (t) { return 1 - Math.pow(1 - t, 2); },
    "power2.out": function (t) { return 1 - Math.pow(1 - t, 3); },
    "power3.out": function (t) { return 1 - Math.pow(1 - t, 4); },
    "power4.out": function (t) { return 1 - Math.pow(1 - t, 5); },
    "power1.in": function (t) { return t * t; },
    "power2.in": function (t) { return t * t * t; },
    "power3.in": function (t) { return t * t * t * t; },
    "power1.inOut": function (t) { return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2; },
    "power2.inOut": function (t) { return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; },
    "power3.inOut": function (t) { return t < 0.5 ? 4 * t * t * t * t : 1 - Math.pow(-2 * t + 2, 4) / 2; },
    "sine.out": function (t) { return Math.sin((t * Math.PI) / 2); },
    "sine.inOut": function (t) { return -(Math.cos(Math.PI * t) - 1) / 2; },
    "back.out": function (t) { var c = 1.70158; return 1 + (c + 1) * Math.pow(t - 1, 3) + c * Math.pow(t - 1, 2); }
  };

  var TRANSFORM_KEYS = { x: 1, y: 1, scale: 1, scaleX: 1, scaleY: 1, rotation: 1 };
  var TRANSFORM_DEFAULT = { x: 0, y: 0, scale: 1, scaleX: 1, scaleY: 1, rotation: 0 };
  var isNum = function (v) { return typeof v === "number" && isFinite(v); };

  function resolve(targets) {
    var out = [];
    if (!targets) return out;
    if (typeof targets === "string") out = Array.prototype.slice.call(document.querySelectorAll(targets));
    else if (targets.nodeType === 1) out.push(targets);
    else if (targets.length) out = Array.prototype.slice.call(targets);
    return out;
  }

  function Timeline() {
    this.tweens = [];
    this.sets = [];
    this.duration = 0;
    this.order = 0;
  }

  Timeline.prototype._add = function (kind, targets, fromProps, toProps, opts) {
    opts = opts || {};
    var at = opts.at == null ? 0 : opts.at;
    var dur = opts.duration == null ? 0.6 : opts.duration;
    var ease = EASES[opts.ease || "power3.out"] || EASES["power3.out"];
    var stagger = opts.stagger || 0;
    var self = this;
    var els = resolve(targets);

    els.forEach(function (el, i) {
      var start = at + i * stagger;
      if (kind === "set") {
        self.sets.push({ el: el, at: start, props: toProps || {} });
        if (start > self.duration) self.duration = start;
        return;
      }
      var from = fromProps ? Object.assign({}, fromProps) : null;
      self.tweens.push({
        el: el,
        from: from,
        to: toProps || {},
        start: start,
        end: start + dur,
        ease: ease,
        order: self.order++,
        origin: opts.transformOrigin || opts.origin || null
      });
      if (start + dur > self.duration) self.duration = start + dur;
    });
    return this;
  };

  Timeline.prototype.fromTo = function (targets, from, to, opts) {
    return this._add("tween", targets, from, to, opts);
  };
  Timeline.prototype.to = function (targets, to, opts) {
    return this._add("tween", targets, null, to, opts);
  };
  Timeline.prototype.set = function (targets, props, at) {
    return this._add("set", targets, null, props, { at: at || 0 });
  };

  Timeline.prototype.seek = function (t) {
    var sorted = this.tweens.slice().sort(function (a, b) {
      return a.start - b.start || a.order - b.order;
    });
    var byEl = new Map();

    sorted.forEach(function (tw) {
      var entry = byEl.get(tw.el);
      if (!entry) {
        entry = { values: Object.create(null), owned: Object.create(null), css: Object.create(null), origin: null };
        byEl.set(tw.el, entry);
      }
      if (tw.origin) entry.origin = tw.origin;

      var keys = Object.keys(tw.to);
      if (tw.from) Object.keys(tw.from).forEach(function (k) { if (keys.indexOf(k) === -1) keys.push(k); });

      keys.forEach(function (key) {
        var toV = tw.to[key];
        var fromV = tw.from ? tw.from[key] : undefined;
        var isTransform = !!TRANSFORM_KEYS[key];

        if (t < tw.start) {
          /* 只在这个属性还没有被任何 tween 接管时，写入初始 from */
          if (!entry.owned[key] && fromV !== undefined) {
            entry.values[key] = fromV;
            if (!isTransform) entry.css[key] = fromV;
          }
          return;
        }

        entry.owned[key] = true;
        var k = t >= tw.end ? 1 : (t - tw.start) / (tw.end - tw.start);
        var e = tw.ease(k);
        var v;
        if (typeof toV === "function") v = toV(e, k);
        else if (isNum(toV)) {
          var base = fromV;
          if (base === undefined) {
            /* .to() 没写 from：优先接续上一条 tween 在该属性上的结束值，
               否则回落到该属性的自然初值（opacity=1、scale=1、x/y/rotation=0）。 */
            if (isNum(entry.values[key])) base = entry.values[key];
            else if (key === "opacity") base = 1;
            else if (isTransform) base = TRANSFORM_DEFAULT[key];
            else base = 0;
          }
          v = base + (toV - base) * e;
        } else v = toV;
        if (v === undefined) return;
        entry.values[key] = v;
        if (!isTransform) entry.css[key] = v;
      });
    });

    byEl.forEach(function (entry, el) {
      if (entry.origin) {
        el.style.transformOrigin = entry.origin;
        el.style.webkitTransformOrigin = entry.origin;
      }
      var p = entry.values;
      var tf = [];
      if ("x" in p) tf.push("translateX(" + p.x + "px)");
      if ("y" in p) tf.push("translateY(" + p.y + "px)");
      if ("scale" in p) tf.push("scale(" + p.scale + ")");
      if ("scaleX" in p) tf.push("scaleX(" + p.scaleX + ")");
      if ("scaleY" in p) tf.push("scaleY(" + p.scaleY + ")");
      if ("rotation" in p) tf.push("rotate(" + p.rotation + "deg)");
      if (tf.length) el.style.transform = tf.join(" ");
      if ("opacity" in p) el.style.opacity = p.opacity;
      Object.keys(entry.css).forEach(function (key) { el.style[key] = entry.css[key]; });
    });

    /* 零时长 set：过点后写入（幂等） */
    this.sets.forEach(function (s) {
      if (t < s.at) return;
      Object.keys(s.props).forEach(function (key) {
        var v = s.props[key];
        if (key === "opacity") s.el.style.opacity = v;
        else if (TRANSFORM_KEYS[key]) {
          var cur = s.el.style.transform || "";
          s.el.style.transform = cur + " " + key + "(" + v + ")";
        } else s.el.style[key] = v;
      });
    });
    return this;
  };

  global.Motion = {
    timeline: function () { return new Timeline(); },
    ease: function (name) { return EASES[name] || EASES["power3.out"]; }
  };
})(typeof window !== "undefined" ? window : this);
