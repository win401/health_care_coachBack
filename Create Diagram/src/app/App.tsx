import { useState } from "react";

type NodeStyle = "blue" | "green" | "amber" | "process" | "db" | "section-end";

interface FNode {
  id: string; x: number; y: number; w: number; h: number;
  label: string; sub?: string; style: NodeStyle; fr?: string;
}

const NODES: FNode[] = [
  { id:"start",           x:330, y:44,   w:220, h:48, label:"[시작] 로그인",          sub:"",                                           style:"blue" },

  // Member ID branch (right side)
  { id:"memberProfile",   x:960, y:175,  w:160, h:48, label:"회원 프로필",             sub:"Member ID 진입",                              style:"blue" },
  { id:"taskCheck",       x:960, y:246,  w:160, h:42, label:"과제 확인",              sub:"FR-021 · assignments",                        style:"process" },
  { id:"scheduleCheck",   x:960, y:306,  w:160, h:42, label:"일정 확인",              sub:"FR-024 · pt_schedules",                       style:"process" },
  { id:"changeCheck",     x:960, y:366,  w:160, h:42, label:"변화기록 확인",           sub:"FR-022 · inbody_metrics",                     style:"process" },
  { id:"home",            x:295, y:136,  w:290, h:52, label:"트레이너 홈화면",         sub:"당일 회원·오늘 일정·최근 기록 로드",                style:"process" },
  { id:"newMember",       x:60,  y:234,  w:195, h:52, label:"신규 회원 등록",          sub:"FR-001 · members, member_profiles",          style:"green" },
  { id:"existingMember",  x:625, y:234,  w:200, h:52, label:"기존 회원 선택",          sub:"FR-002, FR-004 · members, sessions",          style:"green" },

  // Stage 1 row
  { id:"profileSave",     x:28,  y:348,  w:148, h:46, label:"기본 프로필 저장",        sub:"FR-001",                                     style:"process" },
  { id:"bodyInput",       x:196, y:348,  w:152, h:46, label:"신체 기준 정보 입력",     sub:"FR-011",                                     style:"process" },
  { id:"joint",           x:368, y:348,  w:152, h:46, label:"관절/비대칭/가동",        sub:"FR-012, FR-013",                             style:"process" },
  { id:"memberDetail",    x:540, y:348,  w:210, h:46, label:"회원 상세 조회 / 이전 기록 확인", sub:"FR-002, FR-004",                      style:"process" },

  { id:"consent",         x:288, y:440,  w:214, h:46, label:"신체관절 정보 수집 안내", sub:"FR-016 · member_consents",                   style:"amber" },

  { id:"sessionBtn",      x:305, y:534,  w:270, h:52, label:"세션시작 버튼",           sub:"신규/기존 회원 흐름 합류",                       style:"blue" },
  { id:"sessionStart",    x:295, y:636,  w:290, h:52, label:"[세션 시작]",             sub:"회원/세션 컨텍스트 생성",                        style:"process" },

  // Left branch (photo)
  { id:"photo",           x:78,  y:744,  w:172, h:46, label:"사진 업로드",             sub:"FR-005 · posture_images",                    style:"process" },
  { id:"yolo",            x:78,  y:842,  w:172, h:46, label:"YOLO로 이미지 분석",      sub:"FR-006 · posture_keypoints",                  style:"process" },
  { id:"jsonLeft",        x:78,  y:940,  w:172, h:46, label:"JSON 형식으로 파싱",      sub:"posture_analysis / posture_scores",           style:"process" },

  // Right branch (audio)
  { id:"audio",           x:626, y:744,  w:186, h:46, label:"음성 녹음 / 세션 메모 입력", sub:"FR-003 · 텍스트 메시·음성 STT",               style:"process" },
  { id:"gpt",             x:626, y:842,  w:186, h:46, label:"GPT-4o 텍스트 추출",      sub:"운동명/횟수/무게/시험 후보",                      style:"amber" },
  { id:"jsonRight",       x:626, y:940,  w:186, h:46, label:"JSON 형식으로 파싱",      sub:"sessions / session_exercises",               style:"process" },

  { id:"confirm",         x:275, y:1040, w:330, h:52, label:"사용자 확인 & 수정",      sub:"트레이너가 분석/기록 후보 검수",                    style:"process" },
  { id:"db1",             x:260, y:1140, w:360, h:74, label:"DB에 저장",               sub:"members · member_body_profiles · posture_analysis · posture_scores · sessions · session_exercises", style:"db" },
  { id:"report",          x:285, y:1268, w:310, h:52, label:"세션요약 리포트 생성",     sub:"FR-010, FR-022 · reports",                    style:"process" },

  { id:"homework",        x:38,  y:1370, w:195, h:46, label:"과제 등록 / 수행 체크",   sub:"FR-009, FR-021",                             style:"process" },
  { id:"inbody",          x:645, y:1370, w:210, h:46, label:"인바디/변화관리 참고",    sub:"FR-017, FR-018, FR-019, FR-020",             style:"process" },

  { id:"db2",             x:260, y:1466, w:360, h:74, label:"DB에 저장",               sub:"feedbacks · assignments · assignment_completions · reports", style:"db" },
  { id:"schedule",        x:614, y:1590, w:186, h:46, label:"다음 일정 / 알림",        sub:"FR-024, FR-026",                             style:"process" },
  { id:"done",            x:275, y:1686, w:330, h:52, label:"[완료]",                  sub:"리포트 확인 및 다음 일정/알림",                    style:"blue" },
];

const NODE_MAP: Record<string, FNode> = {};
NODES.forEach(n => { NODE_MAP[n.id] = n; });

function cx(n: FNode) { return n.x + n.w / 2; }
function cy(n: FNode) { return n.y + n.h / 2; }
function top(n: FNode)    { return { x: cx(n), y: n.y }; }
function bottom(n: FNode) { return { x: cx(n), y: n.y + n.h }; }
function left(n: FNode)   { return { x: n.x, y: cy(n) }; }
function right(n: FNode)  { return { x: n.x + n.w, y: cy(n) }; }

function line(x1:number,y1:number,x2:number,y2:number){ return `M${x1},${y1} L${x2},${y2}`; }
function curve(x1:number,y1:number,x2:number,y2:number,ctl?:{cx1?:number,cy1?:number,cx2?:number,cy2?:number}){
  const mx=(x1+x2)/2, my=(y1+y2)/2;
  const c1x=ctl?.cx1??mx, c1y=ctl?.cy1??y1, c2x=ctl?.cx2??mx, c2y=ctl?.cy2??y2;
  return `M${x1},${y1} C${c1x},${c1y} ${c2x},${c2y} ${x2},${y2}`;
}

function n(id: string) { return NODE_MAP[id]; }

// Each edge: [path, optional label, labelMidX, labelMidY]
type Edge = { d: string; label?: string; lx?: number; ly?: number };

function buildEdges(): Edge[] {
  const es: Edge[] = [];

  const add = (d: string, label?: string, lx?: number, ly?: number) =>
    es.push({ d, label, lx, ly });

  // start → home (Trainer ID)
  const sb = bottom(n("start")), ht = top(n("home"));
  add(line(sb.x, sb.y, ht.x, ht.y), "Trainer ID", sb.x - 42, (sb.y + ht.y) / 2);

  // start → memberProfile (Member ID) — arc to the right
  const sr = right(n("start")), mpt = top(n("memberProfile"));
  add(curve(sr.x, sr.y, mpt.x, mpt.y, { cx1: sr.x + 80, cy1: sr.y, cx2: mpt.x, cy2: mpt.y - 30 }), "Member ID", sr.x + 54, sr.y - 10);

  // memberProfile → taskCheck → scheduleCheck → changeCheck
  add(line(bottom(n("memberProfile")).x, bottom(n("memberProfile")).y, top(n("taskCheck")).x, top(n("taskCheck")).y));
  add(line(bottom(n("taskCheck")).x, bottom(n("taskCheck")).y, top(n("scheduleCheck")).x, top(n("scheduleCheck")).y));
  add(line(bottom(n("scheduleCheck")).x, bottom(n("scheduleCheck")).y, top(n("changeCheck")).x, top(n("changeCheck")).y));

  // home → newMember / existingMember
  const hb = bottom(n("home"));
  const nmt = top(n("newMember")), emt = top(n("existingMember"));
  add(curve(hb.x, hb.y, nmt.x, nmt.y, { cy1: hb.y+20, cx1: hb.x, cx2: nmt.x, cy2: nmt.y-20 }));
  add(curve(hb.x, hb.y, emt.x, emt.y, { cy1: hb.y+20, cx1: hb.x, cx2: emt.x, cy2: emt.y-20 }));

  // newMember → profileSave
  const nmb = bottom(n("newMember")), pst = top(n("profileSave"));
  add(curve(nmb.x, nmb.y, pst.x, pst.y, { cy1: nmb.y+18, cx1: nmb.x, cx2: pst.x, cy2: pst.y-18 }));

  // Stage 1 horizontal arrows
  const psr = right(n("profileSave")), bil = left(n("bodyInput"));
  add(line(psr.x, psr.y, bil.x, bil.y));
  const bir = right(n("bodyInput")), jol = left(n("joint"));
  add(line(bir.x, bir.y, jol.x, jol.y));
  const jor = right(n("joint")), mdl = left(n("memberDetail"));
  add(line(jor.x, jor.y, mdl.x, mdl.y));

  // existingMember → memberDetail
  const emb = bottom(n("existingMember")), mdt = top(n("memberDetail"));
  add(curve(emb.x, emb.y, mdt.x, mdt.y, { cy1: emb.y+18, cx1: emb.x, cx2: mdt.x, cy2: mdt.y-18 }));

  // joint → consent
  const job = bottom(n("joint")), cnt = top(n("consent"));
  add(curve(job.x, job.y, cnt.x, cnt.y, { cy1: job.y+18, cx1: job.x, cx2: cnt.x, cy2: cnt.y-18 }));

  // consent → sessionBtn
  const cnb = bottom(n("consent")), sbt = top(n("sessionBtn"));
  add(curve(cnb.x, cnb.y, sbt.x, sbt.y, { cy1: cnb.y+15, cx1: cnb.x, cx2: sbt.x, cy2: sbt.y-15 }));

  // memberDetail → sessionBtn (down then left)
  const mdb = bottom(n("memberDetail"));
  const sbr = right(n("sessionBtn"));
  const midY = (mdb.y + sbr.y) / 2;
  add(`M${mdb.x},${mdb.y} L${mdb.x},${sbr.y} C${mdb.x},${sbr.y} ${mdb.x-20},${sbr.y} ${sbr.x},${sbr.y}`);

  // sessionBtn → sessionStart
  const sbBot = bottom(n("sessionBtn")), sst = top(n("sessionStart"));
  add(line(sbBot.x, sbBot.y, sst.x, sst.y));

  // sessionStart → photo / audio (fork)
  const ssb = bottom(n("sessionStart"));
  const pht = top(n("photo")), aut = top(n("audio"));
  add(curve(ssb.x, ssb.y, pht.x, pht.y, { cy1: ssb.y+20, cx1: ssb.x, cx2: pht.x, cy2: pht.y-20 }));
  add(curve(ssb.x, ssb.y, aut.x, aut.y, { cy1: ssb.y+20, cx1: ssb.x, cx2: aut.x, cy2: aut.y-20 }));

  // Photo chain
  add(line(bottom(n("photo")).x, bottom(n("photo")).y, top(n("yolo")).x, top(n("yolo")).y));
  add(line(bottom(n("yolo")).x, bottom(n("yolo")).y, top(n("jsonLeft")).x, top(n("jsonLeft")).y));

  // Audio chain
  add(line(bottom(n("audio")).x, bottom(n("audio")).y, top(n("gpt")).x, top(n("gpt")).y));
  add(line(bottom(n("gpt")).x, bottom(n("gpt")).y, top(n("jsonRight")).x, top(n("jsonRight")).y));

  // jsonLeft → confirm (bottom-left → left side merge)
  const jlb = bottom(n("jsonLeft")), cfl = left(n("confirm"));
  add(`M${jlb.x},${jlb.y} L${jlb.x},${cfl.y} L${cfl.x},${cfl.y}`);

  // jsonRight → confirm (bottom-right → right side merge)
  const jrb = bottom(n("jsonRight")), cfr = right(n("confirm"));
  add(`M${jrb.x},${jrb.y} L${jrb.x},${cfr.y} L${cfr.x},${cfr.y}`);

  // confirm → db1 → report
  add(line(bottom(n("confirm")).x, bottom(n("confirm")).y, top(n("db1")).x, top(n("db1")).y));
  add(line(bottom(n("db1")).x, bottom(n("db1")).y, top(n("report")).x, top(n("report")).y));

  // report → homework (fork left)
  const rpb = bottom(n("report")), hwt = top(n("homework"));
  add(curve(rpb.x, rpb.y, hwt.x, hwt.y, { cy1: rpb.y+18, cx1: rpb.x, cx2: hwt.x, cy2: hwt.y-18 }));

  // report → inbody (fork right)
  const ibt = top(n("inbody"));
  add(curve(rpb.x, rpb.y, ibt.x, ibt.y, { cy1: rpb.y+18, cx1: rpb.x, cx2: ibt.x, cy2: ibt.y-18 }));

  // homework → db2
  const hwb = bottom(n("homework")), db2l = left(n("db2"));
  add(`M${hwb.x},${hwb.y} L${hwb.x},${db2l.y} L${db2l.x},${db2l.y}`);

  // inbody → db2
  const ibb = bottom(n("inbody")), db2r = right(n("db2"));
  add(`M${ibb.x},${ibb.y} L${ibb.x},${db2r.y} L${db2r.x},${db2r.y}`);

  // db2 → memberProfile (profile update loop)
  const db2bForProfile = bottom(n("db2")), mpb = bottom(n("memberProfile"));
  add(`M${db2bForProfile.x},${db2bForProfile.y} L${db2bForProfile.x},1560 L920,1560 L920,${mpb.y + 10} L${mpb.x},${mpb.y + 10}`);

  // db2 → schedule
  const db2bot = bottom(n("db2")), schl = left(n("schedule"));
  add(`M${db2bot.x},${db2bot.y} L${db2bot.x},${schl.y} C${db2bot.x},${schl.y} ${db2bot.x+20},${schl.y} ${schl.x},${schl.y}`);

  // db2 → done (center)
  add(line(bottom(n("db2")).x, bottom(n("db2")).y, top(n("done")).x, top(n("done")).y));

  // schedule → done
  const schb = bottom(n("schedule")), doner = right(n("done"));
  add(`M${schb.x},${schb.y} L${schb.x},${doner.y} L${doner.x},${doner.y}`);

  return es;
}

const EDGES = buildEdges();

const STYLE_MAP: Record<NodeStyle, { fill: string; stroke: string; textColor: string; subColor: string }> = {
  blue:        { fill: "#1d4ed8", stroke: "#1e3a8a", textColor: "#fff",     subColor: "#bfdbfe" },
  green:       { fill: "#f0fdf4", stroke: "#4ade80", textColor: "#15803d",  subColor: "#86efac" },
  amber:       { fill: "#fffbeb", stroke: "#fcd34d", textColor: "#92400e",  subColor: "#fde68a" },
  process:     { fill: "#ffffff", stroke: "#cbd5e1", textColor: "#1e293b",  subColor: "#94a3b8" },
  db:          { fill: "#f0f9ff", stroke: "#7dd3fc", textColor: "#0c4a6e",  subColor: "#38bdf8" },
  "section-end":{ fill:"#f8fafc",stroke:"#e2e8f0",  textColor:"#334155",   subColor:"#94a3b8" },
};

function wrapText(text: string, maxLen: number): string[] {
  if (text.length <= maxLen) return [text];
  const words = text.split(" ");
  const lines: string[] = [];
  let cur = "";
  for (const w of words) {
    if ((cur + " " + w).trim().length > maxLen) {
      if (cur) lines.push(cur.trim());
      cur = w;
    } else {
      cur = (cur + " " + w).trim();
    }
  }
  if (cur) lines.push(cur.trim());
  return lines;
}

function NodeBox({ node }: { node: FNode }) {
  const s = STYLE_MAP[node.style];
  const rdb = node.style === "db";
  const isBlue = node.style === "blue";
  const rx = rdb ? 6 : isBlue ? 10 : 7;

  const labelLines = wrapText(node.label, node.w < 180 ? 16 : 22);
  const subLines = node.sub ? wrapText(node.sub.replace(/·/g, "·"), node.w < 180 ? 22 : 38) : [];

  const totalLines = labelLines.length + (subLines.length > 0 ? 0.4 + subLines.length * 0.85 : 0);
  const labelStartY = cy(node) - (totalLines / 2 - 0.5) * 14 + 1;

  return (
    <g>
      {/* Shadow */}
      <rect x={node.x+2} y={node.y+3} width={node.w} height={node.h} rx={rx} fill="rgba(0,0,0,0.06)" />
      {/* Body */}
      <rect x={node.x} y={node.y} width={node.w} height={node.h} rx={rx}
        fill={s.fill} stroke={s.stroke} strokeWidth={isBlue ? 0 : 1.5}
      />
      {/* DB accent line on top */}
      {rdb && (
        <rect x={node.x} y={node.y} width={node.w} height={4} rx={rx}
          fill="#38bdf8" />
      )}
      {/* Label */}
      {labelLines.map((line, i) => (
        <text key={i}
          x={cx(node)} y={labelStartY + i * 14}
          textAnchor="middle" dominantBaseline="middle"
          fontSize={11.5} fontWeight={600} fill={s.textColor}
          fontFamily="Inter, sans-serif"
        >{line}</text>
      ))}
      {/* Sub label */}
      {subLines.map((sl, i) => (
        <text key={i}
          x={cx(node)} y={labelStartY + labelLines.length * 14 + 4 + i * 12}
          textAnchor="middle" dominantBaseline="middle"
          fontSize={9} fontWeight={400} fill={s.subColor}
          fontFamily="JetBrains Mono, monospace"
        >{sl}</text>
      ))}
    </g>
  );
}

function Arrow({ d }: { d: string }) {
  return (
    <path d={d} fill="none" stroke="#94a3b8" strokeWidth={1.5}
      markerEnd="url(#arrow)" strokeLinejoin="round" />
  );
}

const ERD_DATA = [
  { fr: "FR-001", name: "회원 프로필 등록",          entity: "members, member_profiles, health_notes" },
  { fr: "FR-002", name: "회원 상세 조회",             entity: "members, sessions, assignments" },
  { fr: "FR-003", name: "회원별 세션 기록 작성",       entity: "sessions, session_exercises, members" },
  { fr: "FR-004", name: "세분 기록 목록 및 이전 기록 확인", entity: "sessions, members, assignments" },
  { fr: "FR-005", name: "회원 사진 업로드",            entity: "posture_images, members" },
  { fr: "FR-006", name: "YOLO 기반 자세 분석",        entity: "posture_analysis, posture_keypoints" },
  { fr: "FR-007", name: "자세 점수 및 시각화",         entity: "posture_analysis, posture_scores" },
  { fr: "FR-008", name: "트레이너 피드백 작성",        entity: "feedbacks, sessions, posture_analysis" },
  { fr: "FR-009", name: "과제 등록",                  entity: "assignments, members" },
  { fr: "FR-010", name: "간단 리포트 생성",            entity: "reports, sessions, feedbacks, assignments" },
  { fr: "FR-011", name: "신체 기준 정보 입력",         entity: "members, member_body_profiles" },
  { fr: "FR-012", name: "관절 기준 정보 입력",         entity: "member_joint_profiles" },
  { fr: "FR-013", name: "좌우 비대칭/가동 범위 기준 입력", entity: "member_joint_profiles, member_health_notes" },
  { fr: "FR-014", name: "관절 점수 기반 자세 분석 보정", entity: "posture_analysis_results, member_joint_profiles" },
  { fr: "FR-015", name: "분석 기준 점수 표시",         entity: "posture_analysis_results, member_body_profiles" },
  { fr: "FR-016", name: "신체관절 정보 수집 안내",     entity: "member_consents, member_joint_profiles" },
  { fr: "FR-017", name: "인바디 입력",                entity: "inbody_records, members" },
  { fr: "FR-018", name: "인바디 변화 비교",            entity: "inbody_records, inbody_metrics" },
  { fr: "FR-019", name: "신체 변화 시각화",            entity: "inbody_metrics" },
  { fr: "FR-020", name: "자세 없수 변화 기록",         entity: "posture_scores, posture_images" },
  { fr: "FR-021", name: "과제 수행 체크",              entity: "assignments, assignment_completions" },
  { fr: "FR-022", name: "회원별 변화 리포트",          entity: "reports, sessions, posture_scores, inbody_metrics" },
  { fr: "FR-023", name: "운동 템플릿",                entity: "exercise_templates, template_items" },
  { fr: "FR-024", name: "일정 관리",                  entity: "pt_schedules, members" },
  { fr: "FR-025", name: "회원 경력/필터",              entity: "members, health_notes" },
  { fr: "FR-026", name: "과제/수업 전 알림",           entity: "notifications, assignments, pt_schedules" },
  { fr: "FR-027", name: "PDF 리포트 출력",             entity: "report_exports, reports" },
  { fr: "FR-028", name: "자세 분석 히스토리 상세 보기", entity: "posture_images, posture_analysis, posture_scores" },
];

export default function App() {
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);
  const SVG_W = 1160;
  const SVG_H = 1800;

  return (
    <div className="size-full flex flex-col overflow-hidden bg-slate-50" style={{ fontFamily: "Inter, sans-serif" }}>
      {/* Header */}
      <header className="shrink-0 bg-white border-b border-slate-200 px-8 py-4 flex items-center justify-between shadow-sm z-10">
        <div>
          <div className="flex items-center gap-2">
            <span className="inline-block w-2.5 h-2.5 rounded-full bg-blue-600" />
            <h1 className="text-base font-semibold text-slate-900">FitNote 통합 Process Flow 다이어그램</h1>
          </div>
          <p className="text-xs text-slate-500 mt-0.5 ml-4.5">신규 회원 등록/기존 회원 선택부터 세션 처리, JSON 파싱, DB 저장, 리포트 생성, 완료까지의 통합 흐름</p>
        </div>
        <div className="flex items-center gap-3 text-xs">
          {[
            { color: "#1d4ed8", label: "주요 단계" },
            { color: "#f0fdf4", border: "#4ade80", label: "회원 분기", text: "#15803d" },
            { color: "#fffbeb", border: "#fcd34d", label: "AI 처리", text: "#92400e" },
            { color: "#f0f9ff", border: "#7dd3fc", label: "DB 저장", text: "#0c4a6e" },
          ].map((item) => (
            <div key={item.label} className="flex items-center gap-1.5">
              <span className="inline-block w-3 h-3 rounded-sm border"
                style={{ background: item.color, borderColor: item.border ?? item.color }} />
              <span className="text-slate-500">{item.label}</span>
            </div>
          ))}
        </div>
      </header>

      {/* Scrollable canvas */}
      <div className="flex-1 overflow-auto">
        <div className="min-w-max px-6 py-6">
          <svg width={SVG_W} height={SVG_H} className="rounded-xl overflow-visible">
            <defs>
              <marker id="arrow" markerWidth={8} markerHeight={8} refX={7} refY={3} orient="auto">
                <path d="M0,0 L0,6 L8,3 z" fill="#94a3b8" />
              </marker>
              <pattern id="dots" width={20} height={20} patternUnits="userSpaceOnUse">
                <circle cx={1} cy={1} r={0.8} fill="#d1d5db" />
              </pattern>
            </defs>

            {/* Background */}
            <rect width={SVG_W} height={SVG_H} fill="url(#dots)" rx={12} />

            {/* ── Section backgrounds ── */}

            {/* Stage 1 section */}
            <rect x={18} y={296} width={746} height={206} rx={10}
              fill="white" stroke="#e2e8f0" strokeWidth={1.5} strokeDasharray="6,4" />
            <text x={30} y={316} fontSize={10} fontWeight={600} fill="#64748b" fontFamily="Inter,sans-serif">
              신규 회원 등록 후 Stage 1. 회원 프로필 세분화 및 분석 기준 준비
            </text>

            {/* Parallel processing section */}
            <rect x={50} y={722} width={790} height={288} rx={10}
              fill="white" stroke="#e2e8f0" strokeWidth={1.5} strokeDasharray="6,4" />
            <text x={62} y={740} fontSize={10} fontWeight={600} fill="#64748b" fontFamily="Inter,sans-serif">
              세션 데이터 수집 (병렬)
            </text>

            {/* Trainer flow main wrapper */}
            <rect x={8} y={28} width={884} height={SVG_H - 56} rx={14}
              fill="none" stroke="#e2e8f0" strokeWidth={1} />

            {/* Member ID section box */}
            <rect x={948} y={130} width={196} height={296} rx={10}
              fill="white" stroke="#bfdbfe" strokeWidth={1.5} strokeDasharray="6,4" />
            <text x={960} y={148} fontSize={10} fontWeight={600} fill="#2563eb" fontFamily="Inter,sans-serif">
              Member ID 플로우
            </text>

            {/* Section label */}
            <text x={460} y={20} textAnchor="middle" fontSize={11} fontWeight={600}
              fill="#1e293b" fontFamily="Inter,sans-serif">
              FitNote Trainer — 회원 프로필 준비 + 세션 처리 통합 흐름
            </text>

            {/* ── Edges ── */}
            {EDGES.map((e, i) => (
              <g key={i}>
                <Arrow d={e.d} />
                {e.label && e.lx !== undefined && e.ly !== undefined && (
                  <text x={e.lx} y={e.ly} fontSize={9.5} fontWeight={600}
                    fill="#2563eb" fontFamily="Inter,sans-serif"
                    textAnchor="middle"
                    style={{ paintOrder: "stroke" } as React.CSSProperties}
                    stroke="white" strokeWidth={3}>
                    {e.label}
                  </text>
                )}
              </g>
            ))}

            {/* ── Nodes ── */}
            {NODES.map(node => (
              <g key={node.id}
                onMouseEnter={() => setHoveredNode(node.id)}
                onMouseLeave={() => setHoveredNode(null)}
                style={{ cursor: "default", opacity: hoveredNode && hoveredNode !== node.id ? 0.7 : 1, transition: "opacity 0.15s" }}>
                <NodeBox node={node} />
              </g>
            ))}

            {/* Annotation note */}
            <rect x={28} y={1750} width={844} height={38} rx={6}
              fill="#fef9c3" stroke="#fcd34d" strokeWidth={1} />
            <text x={40} y={1764} fontSize={9.5} fill="#92400e" fontFamily="Inter,sans-serif">
              참고 범례: GPT-4o 텍스트 추출, JSON 파싱, DB 저장 구조를 세션 처리 플로우에 통합.
            </text>
            <text x={40} y={1778} fontSize={9.5} fill="#92400e" fontFamily="Inter,sans-serif">
              실제 STT/리포트 진단은 MVP 범위 밖이며 텍스트 메모 입력으로 대체 가능.
            </text>
          </svg>

          {/* ERD Table */}
          <div className="mt-10 max-w-[900px]">
            <h2 className="text-sm font-semibold text-slate-800 mb-4">각주: 기능요구사항별 ERD 후보 엔티티</h2>
            <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
              <table className="w-full text-xs">
                <thead>
                  <tr className="bg-slate-50 border-b border-slate-200">
                    <th className="text-left px-4 py-3 font-semibold text-slate-600 w-20">FR-ID</th>
                    <th className="text-left px-4 py-3 font-semibold text-slate-600 w-52">기능명</th>
                    <th className="text-left px-4 py-3 font-semibold text-slate-600">엔티티 후보</th>
                  </tr>
                </thead>
                <tbody>
                  {ERD_DATA.map((row, i) => (
                    <tr key={row.fr} className={i % 2 === 0 ? "bg-white" : "bg-slate-50/60"}>
                      <td className="px-4 py-2.5 font-mono font-medium text-blue-700">{row.fr}</td>
                      <td className="px-4 py-2.5 text-slate-700">{row.name}</td>
                      <td className="px-4 py-2.5 text-slate-500 font-mono text-[10.5px]">{row.entity}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
