document.addEventListener("DOMContentLoaded", () => {

    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${protocol}//${window.location.host}/ws/dashboard`;
    let ws;

    // UI Elements
    const views = document.querySelectorAll('.view-section');
    const navItems = document.querySelectorAll('.nav-item[data-target]');

    const valEarnings = document.getElementById("dash-earnings");
    const valBlocked = document.getElementById("dash-blocked");
    const pingFeed = document.getElementById("ping-feed");
    const ledgerList = document.getElementById("ledger-list");
    const protectionPill = document.getElementById("protection-pill");

    // NPU UI Elements
    const npuDot = document.getElementById("npu-dot");
    const npuText = document.getElementById("npu-text");
    const npuBar = document.getElementById("npu-bar");

    let jobsSecured = 0;
    let gigsBlocked = 0;

    // 1. NAVIGATION LOGIC
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            navItems.forEach(n => n.classList.remove('active'));
            views.forEach(v => v.classList.remove('active'));

            item.classList.add('active');
            const target = document.getElementById(item.getAttribute('data-target'));
            target.classList.add('active');
        });
    });

    // 2. DEMO DRAWER LOGIC
    const demoTrigger = document.getElementById('demo-menu-trigger');
    const demoOverlay = document.getElementById('demo-overlay');

    demoTrigger.addEventListener('click', () => demoOverlay.classList.add('visible'));
    demoOverlay.addEventListener('click', (e) => {
        if (e.target === demoOverlay) demoOverlay.classList.remove('visible');
    });

    // 3. TOAST SYSTEM
    function showToast(msg, type = 'sys', icon = 'information-circle') {
        const wrap = document.createElement('div');
        wrap.className = `toast ${type}`;
        wrap.innerHTML = `<ion-icon name="${icon}"></ion-icon><div>${msg}</div>`;
        document.getElementById('toast-container').appendChild(wrap);

        setTimeout(() => {
            wrap.style.opacity = '0';
            wrap.style.transform = 'scale(0.95)';
            wrap.style.transition = '0.3s ease';
            setTimeout(() => wrap.remove(), 300);
        }, 3500);
    }

    // 4. WEBSOCKET LOGIC
    function connectWebSocket() {
        ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            document.getElementById("connection-text").textContent = "AMD Edge Connected";
            document.getElementById("connection-text").style.color = "var(--color-success)";
            showToast("System tracking active via Smartphone Sensors.", "sys", "hardware-chip");
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                handleData(data);
            } catch (e) { console.error(e); }
        };

        ws.onclose = () => {
            document.getElementById("connection-text").textContent = "Connection Severed";
            document.getElementById("connection-text").style.color = "var(--color-danger)";
            setTimeout(connectWebSocket, 3000);
        };
    }

    function handleData(data) {
        if (data.type === "state_update") {
            // Live Earnings sync
            if (data.payload.daily_earnings !== undefined) {
                valEarnings.textContent = parseFloat(data.payload.daily_earnings).toFixed(2);
            }

            // Sync Fatigue Override Status
            if (data.payload.BLOCK_HIGH_STRESS_ORDERS) {
                // Flash protection UI dynamically
                protectionPill.classList.add('fatigued');
                protectionPill.innerHTML = `<ion-icon name="warning"></ion-icon> Driver Fatigue Block`;

                npuDot.className = "dot pulse-red";
                npuText.textContent = "Exhausted (High Stress)";
                npuBar.className = "bar active-bar danger";
            } else {
                protectionPill.classList.remove('fatigued');
                protectionPill.innerHTML = `<ion-icon name="shield"></ion-icon> AI Auto-Reject Active`;

                npuDot.className = "dot pulse-green";
                npuText.textContent = "Optimal (Active)";
                npuBar.className = "bar h-20 active-bar";
            }
        }
        else if (data.type === "log") {
            parseBackendAction(data.message, data.level);
        }
        else if (data.type === "ledger_entry") {
            appendLedgerRow(data.payload);
            if (typeof dynamicAppendToProfileState === "function") {
                dynamicAppendToProfileState(data.payload);
            }
        }
        else if (data.type === "multi_ping_result") {
            renderMultiPingComparison(data.payload);
        }
    }

    // 5. PARSE BACKEND GIG EVENTS
    // Create an explicit queue to bundle simulated states
    let pendingGig = null;

    function parseBackendAction(message, level) {
        const emptyState = pingFeed.querySelector('.empty-feed');
        if (emptyState) emptyState.remove();

        if (level === "system" && message.includes("Intercepted")) {
            // E.g., "[Android Scraper] Intercepted: New Uber ping! Distance: 4.2 km. Payout: ₹180"
            const platform = message.includes("Zomato") ? "Zomato" : "Uber";
            const extPayout = message.match(/₹\s*(\d+)/);
            const extDist = message.match(/(\d+\.?\d*)\s*km/);

            pendingGig = {
                platform: platform,
                payout: extPayout ? extPayout[1] : "??",
                distance: extDist ? extDist[1] : "??"
            };
        }
        else if (level === "opt-accept" && pendingGig) {
            renderGigCard(pendingGig, true, "RHR Analyzed: Highly Profitable");
            pendingGig = null;
        }
        else if (level === "opt-reject" && pendingGig) {
            let reason = "RHR Analyzed: Unprofitable Loss-Maker";
            if (document.getElementById("protection-pill").classList.contains("fatigued")) {
                reason = "Blocked: High Stress Biometrics Active";
            }
            renderGigCard(pendingGig, false, reason);
            gigsBlocked += 1;
            valBlocked.textContent = gigsBlocked;
            pendingGig = null;
        }
        else if (level === "sentinel-warn") {
            showToast("Phone sensors detected erratic motion. Rest induced.", "warn", "warning");
        }
        else if (level === "fiduciary") {
            showToast("Job payment verified and linked via UPI.", "fid", "lock-closed");
        }
    }

    function renderGigCard(gig, isAccept, reasonText) {
        const card = document.createElement('div');
        card.className = `ping-card ${isAccept ? 'accept' : 'reject'}`;

        const platColor = gig.platform === "Zomato" ? "#ef4444" : "white";
        const iconName = isAccept ? "checkmark-circle" : "close-circle";

        card.innerHTML = `
            <div class="p-head">
                <div class="p-platform">
                    <ion-icon name="briefcase" style="color:${platColor}"></ion-icon> 
                    <span>${gig.platform} Ping</span>
                </div>
                <div class="p-price">₹${gig.payout}</div>
            </div>
            <div class="p-body">
                <div class="p-metric"><ion-icon name="compass-outline"></ion-icon> ${gig.distance} km</div>
                <div class="p-metric"><ion-icon name="time-outline"></ion-icon> ~${(gig.distance * 3).toFixed(1)} mins</div>
            </div>
            <div class="p-decision ${isAccept ? 'accept' : 'reject'}">
                <ion-icon name="${iconName}"></ion-icon> ${reasonText}
            </div>
        `;

        pingFeed.prepend(card);
    }

    function renderMultiPingComparison(result) {
        const emptyState = pingFeed.querySelector('.empty-feed');
        if (emptyState) emptyState.remove();

        const wrap = document.createElement('div');
        wrap.style.background = "linear-gradient(145deg, rgba(30,58,138,0.2) 0%, rgba(15,23,42,0.8) 100%)";
        wrap.style.border = "1px solid rgba(59,130,246,0.4)";
        wrap.style.borderRadius = "16px";
        wrap.style.padding = "16px";
        wrap.style.marginBottom = "16px";
        wrap.style.animation = "fadeUp 0.3s";

        let html = `
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
                <h4 style="color:white; font-size:0.95rem; display:flex; align-items:center; gap:8px;">
                    <ion-icon name="flash" style="color:#fbbf24;"></ion-icon> Multi-Platform Scraper
                </h4>
                <div style="background:rgba(59,130,246,0.2); color:#60a5fa; font-size:0.7rem; padding:4px 8px; border-radius:12px; font-weight:700;">
                    Algorithm War
                </div>
            </div>
            <div style="display:flex; flex-direction:column; gap:8px; margin-bottom:16px;">
        `;

        if (!result.all_parsed || result.all_parsed.length === 0) return;

        // Render each ping
        result.all_parsed.forEach(ping => {
            const isWinner = result.decision === "ACCEPT_BEST" && result.selected.platform === ping.platform;
            const border = isWinner ? "border:1px solid var(--color-success);" : "border:1px solid rgba(255,255,255,0.05);";
            const bg = isWinner ? "background:rgba(16,185,129,0.1);" : "background:var(--bg-card);";
            const badge = isWinner ? `<span style="background:var(--color-success); color:white; font-size:0.6rem; padding:2px 6px; border-radius:4px; margin-left:8px;">WINNER</span>` : '';

            html += `
                <div style="${bg} ${border} border-radius:12px; padding:12px; display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <div style="font-size:0.8rem; color:white; font-weight:700; display:flex; align-items:center;">
                            ${ping.platform} ${badge}
                        </div>
                        <div style="font-size:0.7rem; color:var(--text-secondary); margin-top:4px;">
                            ${ping.distance} km | RHR: ₹${ping.rhr.toFixed(0)}/hr
                        </div>
                    </div>
                    <div style="font-size:1.1rem; color:white; font-weight:800;">₹${ping.payout}</div>
                </div>
            `;
        });

        html += `</div>`;

        if (result.decision === "ACCEPT_BEST") {
            html += `
                <div style="background:var(--color-success); color:black; padding:10px; border-radius:8px; font-size:0.8rem; font-weight:700; display:flex; align-items:center; gap:8px;">
                    <ion-icon name="checkmark-circle"></ion-icon> Accepted highest RHR route. Bank notified.
                </div>
            `;
        } else {
            html += `
                <div style="background:rgba(239,68,68,0.2); color:#fca5a5; padding:10px; border-radius:8px; font-size:0.8rem; font-weight:700; border:1px solid rgba(239,68,68,0.3); display:flex; align-items:center; gap:8px;">
                    <ion-icon name="close-circle"></ion-icon> All options unprofitable. Ignored.
                </div>
            `;
        }

        wrap.innerHTML = html;
        pingFeed.prepend(wrap);
    }

    function appendLedgerRow(record) {
        const emptyState = ledgerList.querySelector('.empty-feed');
        if (emptyState) emptyState.remove();

        const el = document.createElement("div");
        el.className = "ledger-item";
        el.style.padding = "14px";
        el.style.borderLeft = "4px solid var(--color-success)";

        const d = new Date(record.data.timestamp);
        const timeStr = d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        const upiRef = record.hash;
        const dist = (record.data.duration_mins / 3.0).toFixed(1);
        const rhr = (record.data.payout_inr / (record.data.duration_mins / 60)).toFixed(0);

        el.innerHTML = `
            <div style="display:flex; justify-content:space-between; width:100%;">
                <div class="l-left">
                    <div class="l-title" style="font-weight:800; color:white;">${record.data.platform} <span style="font-weight:400; font-size:0.7rem; color:var(--text-secondary)">Delivery Identity</span></div>
                    <div style="font-size:0.65rem; color:var(--accent-light); margin:2px 0;">Ref: ${upiRef}</div>
                    
                    <div style="display:flex; gap:12px; margin-top:6px;">
                        <div style="font-size:0.65rem; color:var(--text-secondary); display:flex; align-items:center; gap:3px;">
                            <ion-icon name="navigate" style="color:var(--color-success)"></ion-icon> ${dist} km
                        </div>
                        <div style="font-size:0.65rem; color:var(--text-secondary); display:flex; align-items:center; gap:3px;">
                            <ion-icon name="flash" style="color:#fbbf24"></ion-icon> ₹${rhr}/hr RHR
                        </div>
                        <div style="font-size:0.65rem; color:var(--text-secondary); display:flex; align-items:center; gap:3px;">
                            <ion-icon name="time-outline"></ion-icon> ${timeStr}
                        </div>
                    </div>
                </div>
                <div style="text-align:right;">
                    <div style="font-weight:900; color:white; font-size:1.1rem;">₹${parseFloat(record.data.payout_inr).toFixed(2)}</div>
                    <div style="font-size:0.6rem; color:var(--color-success); font-weight:700;">Verified Income</div>
                </div>
            </div>
        `;

        ledgerList.prepend(el);
    }

    document.getElementById("btn-download-ledger").addEventListener("click", () => {
        showToast("Generating Verifiable PDF Certificate...", "sys", "cloud-download");
        setTimeout(() => {
            showToast("Work-Proof Identity Secured.", "sys", "checkmark-done-circle");
        }, 1500);
    });

    // 7. PROFILE LOGIC & LOGS
    const profileBtn = document.getElementById('btn-profile');
    const profileOverlay = document.getElementById('profile-overlay');
    const btnCloseProfile = document.getElementById('btn-close-profile');
    const monthSelector = document.getElementById('month-selector');

    // Create robust mock data associated with months
    let gigDatabase = [
        { date: new Date("2026-10-24T14:30:00"), platform: "Uber", payout: 240, id: "UPI109283748255", dist: 8.5 },
        { date: new Date("2026-10-24T10:15:00"), platform: "Zomato", payout: 85, id: "UPI998822331100", dist: 3.2 },
        { date: new Date("2026-10-23T18:45:00"), platform: "Rapido", payout: 110, id: "UPI776655443322", dist: 5.0 },
        { date: new Date("2026-09-15T09:00:00"), platform: "Uber", payout: 450, id: "UPI564738291022", dist: 16.0 },
        { date: new Date("2026-09-12T20:30:00"), platform: "Swiggy", payout: 60, id: "UPI847563029188", dist: 2.1 }
    ];

    window.dynamicAppendToProfileState = function (payload) {
        gigDatabase.unshift({
            date: new Date(),
            platform: payload.data.platform,
            payout: payload.data.payout_inr,
            id: payload.hash,
            dist: payload.data.duration_mins / 3.0 // reverse engineered mock mock estimation
        });
        if (profileOverlay.classList.contains('visible')) {
            renderProfileLogs();
        }
    }

    function renderProfileLogs() {
        const gigLogDiv = document.getElementById("monthly-gig-logs");
        const petrolLogDiv = document.getElementById("monthly-petrol-logs");
        const selectedMonth = parseInt(monthSelector.value);

        // Filter the database for the selected month
        const filteredGigs = gigDatabase.filter(g => g.date.getMonth() === selectedMonth);

        // Render logs
        if (filteredGigs.length === 0) {
            gigLogDiv.innerHTML = `<div style="text-align:center; padding: 20px; color:var(--text-secondary);">No verifiable deliveries completed in this month.</div>`;
        } else {
            gigLogDiv.innerHTML = filteredGigs.map(g => {
                const day = g.date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
                return `
                <div style="display:flex; justify-content:space-between; margin-bottom:8px; border-bottom:1px solid rgba(255,255,255,0.1); padding-bottom:4px;">
                    <div style="display:flex; flex-direction:column;">
                        <span><strong>${g.platform}</strong> <span style="font-size:0.7rem; color:var(--text-secondary)">${day}</span></span>
                        <span style="font-size:0.6rem; color:#60a5fa">${g.id}</span>
                    </div>
                    <div style="font-weight:bold;">₹${parseFloat(g.payout).toFixed(2)}</div>
                </div>
                `;
            }).join('');
        }

        // Render petrol calculations
        const petrolCost = parseFloat(document.getElementById("input-petrol").value) || 2.5;
        let totalDist = 0;
        filteredGigs.forEach(g => { totalDist += (g.dist || 0); });

        // Add a base operational distance penalty of 20km if there are gigs
        if (filteredGigs.length > 0) totalDist += 20;

        const estimatedSpend = totalDist * petrolCost;

        petrolLogDiv.innerHTML = `
            <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                <div><strong>Current Rate</strong></div>
                <div>₹${petrolCost} / km</div>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:8px; color:var(--text-secondary);">
                <div>Total Monthly Distance Logged</div>
                <div>${totalDist.toFixed(1)} km</div>
            </div>
            <div style="display:flex; justify-content:space-between; margin-top:8px; padding-top:8px; border-top:1px solid rgba(255,255,255,0.1); color:var(--color-danger); font-weight:bold;">
                <div>Estimated Monthly Spend</div>
                <div>- ₹${estimatedSpend.toFixed(2)}</div>
            </div>
        `;
    }

    if (monthSelector) {
        monthSelector.addEventListener('change', renderProfileLogs);
    }

    if (profileBtn) {
        profileBtn.addEventListener('click', () => {
            // Auto-select current month when opening
            const currentMonth = new Date().getMonth();
            monthSelector.value = currentMonth;

            renderProfileLogs();
            profileOverlay.classList.add('visible');
        });
    }
    if (btnCloseProfile) {
        btnCloseProfile.addEventListener('click', () => {
            profileOverlay.classList.remove('visible');
        });
    }
    if (profileOverlay) {
        profileOverlay.addEventListener('click', (e) => {
            if (e.target === profileOverlay) profileOverlay.classList.remove('visible');
        });
    }

    // 8. BUTTON EVENT BINDINGS FOR DEMO
    document.getElementById("btn-ping-good").addEventListener("click", () => {
        demoOverlay.classList.remove('visible');

        // This math intentionally evaluates to an RHR that triggers ACCEPT in python backend
        // e.g., payout=220, dist=4.2 -> roughly 500+ RHR vs 172.5 threshold
        fetch("/api/simulate_ping", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ raw_screen_text: "UberX: Distance 4.2 km. Payout: ₹220.", source: "dashboard_demo" })
        });

        // Automatically switch over to the Feed Tab to view it happen
        navItems[1].click();
    });

    document.getElementById("btn-ping-bad").addEventListener("click", () => {
        demoOverlay.classList.remove('visible');

        // This math intentionally evaluates to REJECT in python backend
        // e.g., payout=40, dist=15.0 -> negative margins due to fuel costs
        fetch("/api/simulate_ping", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ raw_screen_text: "Zomato: Distance 15.0 km. Payout: ₹40.", source: "dashboard_demo" })
        });

        navItems[1].click();
    });

    document.getElementById("btn-fatigue").addEventListener("click", () => {
        demoOverlay.classList.remove('visible');
        fetch("/api/simulate_fatigue", { method: "POST" });
        navItems[0].click(); // Stay on Hub to see the Biometric sensor flip
    });

    document.getElementById("btn-reset").addEventListener("click", () => {
        demoOverlay.classList.remove('visible');
        fetch("/api/reset_systems", { method: "POST" });
        showToast("Systems recalibrated. Drive safe!", "sys", "refresh-circle");
    });

    document.getElementById("btn-multi-ping").addEventListener("click", () => {
        demoOverlay.classList.remove('visible');

        const payload = {
            pings: [
                { platform: "Uber", text: "UberX ping! Distance: 4.5 km. Payout: ₹120" },
                { platform: "Zomato", text: "Zomato ping! Distance: 2.1 km. Payout: ₹95" },  // Best RHR
                { platform: "Rapido", text: "Rapido ping! Distance: 6.0 km. Payout: ₹100" }
            ]
        };

        fetch("/api/simulate_multi_ping", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        navItems[1].click(); // Switch to scraper
    });

    document.getElementById("btn-save-petrol").addEventListener("click", () => {
        const cost = document.getElementById("input-petrol").value;
        fetch("/api/set_config", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ petrol_cost: cost })
        });
        showToast("RHR Algorithm Updated securely.", "sys", "construct-outline");
    });

    document.getElementById("toggle-npu").addEventListener("change", (e) => {
        const val = e.target.checked ? "npu_capable" : "basic_cloud";
        const text = e.target.checked ? "Smartphone Motion Sensors" : "Basic Activity Tracking";
        document.getElementById("hardware-mode-text").textContent = text;

        if (!e.target.checked) document.getElementById("npu-dot").className = "dot";
        else document.getElementById("npu-dot").className = "dot pulse-green";

        fetch("/api/set_config", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ device_capability: val })
        });
    });

    connectWebSocket();
});
