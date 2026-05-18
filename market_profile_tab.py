# ════════════════════════════════════════════════════════════════════════
#  TAB 4 — MARKET PROFILE  + DAY-OVER-DAY VALUE MIGRATION
#  Append this entire block to the END of app.py
# ════════════════════════════════════════════════════════════════════════
#
#  INTEGRATION — two edits only, nothing else in app.py changes:
#
#  1) Find (~line 1208):
#         tab1, tab2, tab3 = st.tabs([
#             "📡  FETCH DATA",
#             "📊  CHART & FORECAST",
#             "🎯  BROOKS LIVE",
#         ])
#     Replace with:
#         tab1, tab2, tab3, tab4 = st.tabs([
#             "📡  FETCH DATA",
#             "📊  CHART & FORECAST",
#             "🎯  BROOKS LIVE",
#             "🗂  MARKET PROFILE",
#         ])
#
#  2) Paste everything below at the end of app.py.
#
#  Reuses st.session_state["fetched_df"] from Tab 1 — NO new API calls,
#  cannot interfere with login / Brooks / autorefresh.
#  For the migration panel, fetch a MULTI-DAY range in Tab 1
#  (the default 7-day range already does this) at 1-min or 3-min.
# ════════════════════════════════════════════════════════════════════════

import string as _mp_string

_MP_LET = _mp_string.ascii_uppercase + _mp_string.ascii_lowercase


def _mp_build_session_profile(day_df, period_min, tick):
    """Build a TPO profile for one session's candles.
    Returns dict with poc, va_low, va_high, ib_lo, ib_hi, rows, periods,
    day_hi, day_lo, regime info — or None if too few candles."""
    day_df = day_df.sort_values("datetime")
    if len(day_df) < 10:
        return None

    sess_start = day_df["datetime"].iloc[0].replace(
        hour=9, minute=15, second=0, microsecond=0)

    def _round_tick(p):
        return round(round(p / tick) * tick, 4)

    def _period_idx(ts):
        mins = (ts - sess_start).total_seconds() / 60.0
        return -1 if mins < 0 else int(mins // period_min)

    per_hi, per_lo = {}, {}
    for _, r in day_df.iterrows():
        pi = _period_idx(r["datetime"])
        if pi < 0 or pi >= len(_MP_LET):
            continue
        per_hi[pi] = max(per_hi.get(pi, r["high"]), r["high"])
        per_lo[pi] = min(per_lo.get(pi, r["low"]), r["low"])

    if not per_hi:
        return None

    rows_tpo, period_ranges = {}, []
    for pi in sorted(per_hi):
        letter = _MP_LET[pi]
        lo = _round_tick(per_lo[pi])
        hi = _round_tick(per_hi[pi])
        period_ranges.append((letter, lo, hi))
        lvl = lo
        while lvl <= hi + 1e-9:
            rows_tpo.setdefault(lvl, set()).add(letter)
            lvl = round(lvl + tick, 4)

    counts = {p: len(s) for p, s in rows_tpo.items()}
    poc = max(counts, key=counts.get)
    total = sum(counts.values())

    prices_asc = sorted(counts)
    poc_i = prices_asc.index(poc)
    lo_i = hi_i = poc_i
    acc = counts[poc]
    target = total * 0.70
    while acc < target and (lo_i > 0 or hi_i < len(prices_asc) - 1):
        up = counts[prices_asc[hi_i + 1]] if hi_i + 1 < len(prices_asc) else -1
        dn = counts[prices_asc[lo_i - 1]] if lo_i - 1 >= 0 else -1
        if up >= dn:
            hi_i = min(hi_i + 1, len(prices_asc) - 1)
            acc += max(up, 0)
        else:
            lo_i = max(lo_i - 1, 0)
            acc += max(dn, 0)
    va_low, va_high = prices_asc[lo_i], prices_asc[hi_i]

    n_ib = max(1, 60 // period_min)
    ib_rows = [r for r in period_ranges if _MP_LET.index(r[0]) < n_ib]
    ib_lo = min(r[1] for r in ib_rows)
    ib_hi = max(r[2] for r in ib_rows)
    ib_range = ib_hi - ib_lo

    day_hi = float(day_df["high"].max())
    day_lo = float(day_df["low"].min())
    ext = max(max(0.0, day_hi - ib_hi), max(0.0, ib_lo - day_lo))
    ratio = (ext / ib_range) if ib_range else 0.0

    if ratio < 0.15:
        regime, regime_c = "ROTATIONAL", "#dc2626"
        regime_msg = ("Price held inside the initial balance. Theta-trap "
                      "day — naked CE/PE buying disfavoured.")
    elif ratio < 0.6:
        regime, regime_c = "NORMAL VARIATION", "#f59e0b"
        regime_msg = ("Moderate range extension. Selective option buys "
                      "only with a fast confirmed trigger.")
    else:
        regime, regime_c = "TREND / DOUBLE-DIST", "#16a34a"
        regime_msg = ("Strong range extension — the directional, "
                      "option-buyable regime. Pair with a trigger.")

    return dict(
        poc=poc, va_low=va_low, va_high=va_high,
        ib_lo=ib_lo, ib_hi=ib_hi, ib_range=ib_range,
        rows=rows_tpo, counts=counts, periods=period_ranges,
        day_hi=day_hi, day_lo=day_lo, ext=ext, ratio=ratio,
        regime=regime, regime_c=regime_c, regime_msg=regime_msg,
        ext_up=(day_hi - ib_hi), ext_dn=(ib_lo - day_lo),
    )


def _mp_value_migration(prev, curr):
    """Classify how value migrated from prev session to curr session.
    This is Dalton's strongest day-over-day directional tell."""
    p_lo, p_hi = prev["va_low"], prev["va_high"]
    c_lo, c_hi = curr["va_low"], curr["va_high"]
    poc_shift = curr["poc"] - prev["poc"]

    overlap = max(0.0, min(p_hi, c_hi) - max(p_lo, c_lo))
    p_width = max(1e-9, p_hi - p_lo)
    overlap_pct = overlap / p_width

    if c_lo > p_hi:
        tag, color = "HIGHER — UNOVERLAPPING", "#16a34a"
        read = ("Strong bullish acceptance. Value built entirely above "
                "yesterday — a gap-and-go style continuation tell. CE "
                "side favoured if a trigger appears.")
    elif c_hi < p_lo:
        tag, color = "LOWER — UNOVERLAPPING", "#dc2626"
        read = ("Strong bearish acceptance. Value built entirely below "
                "yesterday. PE side favoured if a trigger appears.")
    elif c_lo > p_lo and c_hi > p_hi:
        tag, color = "OVERLAPPING-TO-HIGHER", "#16a34a"
        read = ("Bullish drift with acceptance — Dalton's cleanest "
                "continuation pattern. Value migrating up while still "
                "connected to yesterday. Favour CE on pullbacks to VAL.")
    elif c_hi < p_hi and c_lo < p_lo:
        tag, color = "OVERLAPPING-TO-LOWER", "#dc2626"
        read = ("Bearish drift with acceptance. Value migrating down "
                "while connected to yesterday. Favour PE on rallies "
                "to VAH.")
    elif overlap_pct > 0.7:
        tag, color = "OVERLAPPING / UNCHANGED", "#64748b"
        read = ("Value essentially unchanged — balance / acceptance of "
                "the same area. Rotational bias; weak day for naked "
                "option buying unless a fresh catalyst breaks balance.")
    else:
        tag, color = "INSIDE / NARROWER", "#64748b"
        read = ("Value contracted inside yesterday's range — balance "
                "tightening, often coils before an expansion. Wait for "
                "the break rather than buying the coil.")

    return dict(tag=tag, color=color, read=read,
                poc_shift=poc_shift, overlap_pct=overlap_pct)


with tab4:
    st.markdown(
        '<div class="card"><div class="card-title">🗂 MARKET PROFILE · TPO</div>',
        unsafe_allow_html=True,
    )

    if "fetched_df" not in st.session_state:
        st.markdown(
            "<div style='text-align:center; padding:2rem 1rem; color:#94a3b8;"
            " font-family:\"JetBrains Mono\",monospace; font-size:0.8rem;"
            " letter-spacing:2px;'>NO DATA LOADED<br>"
            "<span style='font-size:0.7rem;'>Fetch a multi-day range in "
            "Tab 1 (1-min or 3-min) for profiles + value migration"
            "</span></div>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        mp_df = st.session_state["fetched_df"].copy()
        mp_sym = st.session_state.get("fetch_symbol", "")
        mp_df["datetime"] = pd.to_datetime(mp_df["datetime"])
        sessions = sorted(mp_df["datetime"].dt.date.unique())

        c1, c2, c3 = st.columns(3)
        with c1:
            sel_day = st.selectbox(
                "Session", sessions, index=len(sessions) - 1,
                format_func=lambda d: d.strftime("%d %b %Y"),
            )
        with c2:
            period_min = st.selectbox(
                "TPO period", [30, 15, 60], index=0,
                help="30 min = classic Dalton. 15 = finer intraday.",
            )
        with c3:
            default_tick = (10.0 if "BANK" in mp_sym.upper()
                            else 5.0 if "NIFTY" in mp_sym.upper() else 1.0)
            tick = st.number_input(
                "Row size (pts)", min_value=0.05,
                value=float(default_tick), step=0.05,
                help="~5 NIFTY · ~10 BANKNIFTY · small for option premiums.",
            )

        st.markdown("</div>", unsafe_allow_html=True)

        day_df = mp_df[mp_df["datetime"].dt.date == sel_day]
        prof = _mp_build_session_profile(day_df, period_min, tick)

        if prof is None:
            st.warning("Not enough candles in this session for a profile.")
        else:
            # ── Structure cards ───────────────────────────────────────
            st.markdown('<div class="card">', unsafe_allow_html=True)
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Point of Control", f"{prof['poc']:,.2f}")
            m2.metric("Value Area",
                      f"{prof['va_low']:,.0f}–{prof['va_high']:,.0f}")
            m3.metric("Initial Balance",
                      f"{prof['ib_lo']:,.0f}–{prof['ib_hi']:,.0f}")
            m4.metric("Range Ext / IB", f"{prof['ratio']:.2f}×")
            st.markdown("</div>", unsafe_allow_html=True)

            # ── Day regime verdict ────────────────────────────────────
            _dir = "↑" if prof["ext_up"] >= prof["ext_dn"] else "↓"
            st.markdown(
                f"<div class='card' style='border-left:4px solid "
                f"{prof['regime_c']};'><div class='card-title' "
                f"style='color:{prof['regime_c']};'>🎯 DAY REGIME · "
                f"{prof['regime']}</div><div style='font-size:0.85rem; "
                f"color:#0f172a; line-height:1.6;'>{prof['regime_msg']}"
                f"</div><div style='font-size:0.72rem; color:#64748b; "
                f"margin-top:8px; font-family:\"JetBrains Mono\","
                f"monospace;'>Extension {prof['ext']:,.1f} pts {_dir} · "
                f"IB range {prof['ib_range']:,.1f} pts · "
                f"{len(prof['periods'])} periods</div></div>",
                unsafe_allow_html=True,
            )

            # ── Day-over-day VALUE MIGRATION ──────────────────────────
            sel_idx = sessions.index(sel_day)
            if sel_idx > 0:
                prev_day = sessions[sel_idx - 1]
                prev_df = mp_df[mp_df["datetime"].dt.date == prev_day]
                prev_prof = _mp_build_session_profile(
                    prev_df, period_min, tick)
                if prev_prof is not None:
                    mig = _mp_value_migration(prev_prof, prof)
                    st.markdown(
                        f"<div class='card' style='border-left:4px solid "
                        f"{mig['color']};'><div class='card-title' "
                        f"style='color:{mig['color']};'>📈 VALUE "
                        f"MIGRATION vs {prev_day.strftime('%d %b')} · "
                        f"{mig['tag']}</div>"
                        f"<div style='font-size:0.85rem; color:#0f172a; "
                        f"line-height:1.6;'>{mig['read']}</div>"
                        f"<div style='font-size:0.72rem; color:#64748b; "
                        f"margin-top:8px; font-family:\"JetBrains "
                        f"Mono\",monospace;'>POC shift "
                        f"{mig['poc_shift']:+,.1f} pts · "
                        f"VA overlap {mig['overlap_pct']*100:,.0f}% · "
                        f"prev VA {prev_prof['va_low']:,.0f}–"
                        f"{prev_prof['va_high']:,.0f}</div></div>",
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown(
                    "<div class='card'><div style='font-size:0.75rem; "
                    "color:#94a3b8; font-family:\"JetBrains Mono\","
                    "monospace; letter-spacing:1px;'>VALUE MIGRATION — "
                    "need a prior session. Fetch a wider date range in "
                    "Tab 1.</div></div>",
                    unsafe_allow_html=True,
                )

            # ── TPO profile chart ─────────────────────────────────────
            rows_tpo = prof["rows"]
            counts = prof["counts"]
            prices_sorted = sorted(rows_tpo)
            bar_counts = [counts[p] for p in prices_sorted]
            bar_text = ["".join(sorted(rows_tpo[p])) for p in prices_sorted]
            bar_colors = [
                "#0ea5e9" if p == prof["poc"]
                else ("#bae6fd"
                      if prof["va_low"] <= p <= prof["va_high"]
                      else "#e2e8f0")
                for p in prices_sorted
            ]

            fig_mp = go.Figure()
            fig_mp.add_trace(go.Bar(
                x=bar_counts, y=prices_sorted, orientation="h",
                text=bar_text, textposition="outside",
                marker=dict(color=bar_colors),
                hovertemplate="Price %{y}<br>%{x} TPOs<extra></extra>",
                cliponaxis=False,
            ))
            for lvl, dash, col, lbl in [
                (prof["poc"], "solid", "#0ea5e9", "POC"),
                (prof["va_high"], "dot", "#0284c7", "VAH"),
                (prof["va_low"], "dot", "#0284c7", "VAL"),
                (prof["ib_hi"], "dash", "#f59e0b", "IB hi"),
                (prof["ib_lo"], "dash", "#f59e0b", "IB lo"),
            ]:
                fig_mp.add_hline(
                    y=lvl, line_dash=dash, line_color=col, line_width=1,
                    annotation_text=lbl, annotation_position="right",
                    annotation_font_size=10, annotation_font_color=col,
                )
            fig_mp.update_layout(
                height=max(420, len(prices_sorted) * 16),
                margin=dict(l=10, r=70, t=20, b=20),
                paper_bgcolor="white", plot_bgcolor="white",
                font=dict(family="JetBrains Mono, monospace",
                          size=10, color="#0f172a"),
                xaxis=dict(title="TPO count", gridcolor="#f1f5f9",
                           zeroline=False),
                yaxis=dict(title="Price", gridcolor="#f8fafc",
                           tickformat=",.0f"),
                showlegend=False, bargap=0.15,
            )
            st.plotly_chart(fig_mp, use_container_width=True)

            with st.expander("How to use this with the edge stack"):
                st.markdown(
                    "**Order of operations for an option-buy decision:**\n\n"
                    "1. **Value migration first.** Overlapping-to-higher / "
                    "higher-unoverlapping = bullish acceptance (CE bias). "
                    "Mirror for PE. Unchanged / inside = rotational, skip.\n"
                    "2. **Day regime second.** ROTATIONAL → theta trap, "
                    "don't buy. TREND / DOUBLE-DIST → option-buyable.\n"
                    "3. **Brooks Live third** for the entry trigger.\n"
                    "4. **Greeks last** — ATM for a fast move, only if "
                    "realized > implied volatility.\n\n"
                    "POC = fair-price magnet. Short single-letter rows = "
                    "rejection tails (stop / fade references). VAH/VAL = "
                    "responsive trade-location levels."
                )
