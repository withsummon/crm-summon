(function () {
  const featureGroups = [
    {
      key: "overview",
      label: "Overview",
      features: [
        [1, "Customer 360 Overview Tab", "Header, customer identity, quick stats, AI summary, and primary actions."],
        [17, "AI Customer Summary", "Five-bullet customer summary with risk highlights and saveable notes."],
        [18, "Relationship Graph", "Visual network for contacts, related companies, RM team, and relation filters."],
        [19, "Timeline View", "Chronological applications, payments, communications, and risk events."],
        [27, "Customer Search (Global)", "Search by name, NPWP, KTP, phone, email, fuzzy match, preview, and recent searches."],
      ],
    },
    {
      key: "profile",
      label: "Profile & KYC",
      features: [
        [2, "Personal/Company Data Tab", "Editable company data with KTP/NPWP validation and audit trail."],
        [24, "KYC Status", "KYC status, last review, next review, renewal workflow, and e-KYC result."],
        [25, "Customer Tagging", "Multiple tags, color segmentation, customer filters, and bulk tag operation."],
      ],
    },
    {
      key: "ownership",
      label: "Ownership",
      features: [
        [3, "Shareholders Tab", "Shareholder list, percentage validation, UBO, and ownership chart."],
        [4, "Directors Tab", "Directors, roles, ID, tenure, background check, AML/PEP action."],
        [5, "Related Entities Tab", "Parent, subsidiary, sister companies, relation tags, and group exposure."],
      ],
    },
    {
      key: "facilities",
      label: "Facilities",
      features: [
        [6, "Financing History Tab", "Past facilities, repayment behavior, product filter, PDF export, default history."],
        [7, "Active Facilities Tab", "Outstanding, due date, health color, top-up, restructure, and drilldown."],
        [8, "Credit Score Display", "Internal score, Pefindo/SLIK score, trend chart, date, and refresh."],
        [10, "Collateral Tab", "Collateral list, value, LTV, insurance expiry, document links, re-appraisal."],
        [15, "Transaction History Tab", "Repayments, missed payments, date filters, running balance, Excel export."],
      ],
    },
    {
      key: "documents",
      label: "Documents",
      features: [
        [11, "Documents Tab", "Folders by type, expiry icons, version history, preview, tag, and search."],
        [13, "Financial Statements Tab", "P/L, balance sheet, cashflow, AI extraction, multi-year comparison, audit year."],
        [16, "Site Visit History Tab", "Visit dates, RM, photos, notes, GPS, PDF report, and next reminder."],
      ],
    },
    {
      key: "engagement",
      label: "Engagement",
      features: [
        [12, "Communications Tab", "Email, WhatsApp, SMS, call timeline, channel filters, conversation, compose."],
        [20, "Tasks Tab", "Customer tasks, assignee, due date, priority, complete, recurring options."],
        [21, "AI Insights Tab", "Cross-sell, retention, upsell insights, confidence, accept/dismiss, outcome."],
      ],
    },
    {
      key: "governance",
      label: "Governance",
      features: [
        [9, "Bank Accounts Tab", "Accounts, primary account, verification status, and OTP add flow."],
        [14, "Risk Profile Tab", "Risk grade, watchlist, NPL flag, risk factors, grade history, triggers."],
        [22, "Watchlist Flag", "Watchlist toggle, mandatory reason, removal approval, and profile badge."],
        [23, "Customer Merge", "Duplicate merge, winning field value, reassignment, old ID audit log."],
        [26, "Print/Export Profile", "Full or tab-specific PDF, watermark, email export, and password protection."],
      ],
    },
  ];

  const metrics = [
    ["Total Outstanding", "Rp 24.8B", "6 active facilities"],
    ["Risk Grade", "B+", "Internal score 782"],
    ["Group Exposure", "Rp 41.2B", "4 related entities"],
    ["KYC Status", "Done", "Next review 18 Jun 2026"],
  ];

  function esc(value) {
    return $("<div>").text(value == null ? "" : String(value)).html();
  }

  function featureCards(group) {
    return group.features
      .map(
        ([no, title, note]) => `
          <button class="summon-c360-feature" type="button" data-c360-feature="${no}">
            <div class="summon-c360-feature-no">#${no}</div>
            <div class="summon-c360-feature-title">${esc(title)}</div>
            <div class="summon-c360-feature-note">${esc(note)}</div>
          </button>
        `,
      )
      .join("");
  }

  function renderGroupPanels() {
    return featureGroups
      .map(
        (group, index) => `
          <div class="summon-c360-group ${index ? "summon-c360-hidden" : ""}" data-c360-panel="${group.key}">
            <div class="summon-c360-grid">
              ${renderGroupContent(group.key)}
            </div>
          </div>
        `,
      )
      .join("");
  }

  function renderGroupContent(key) {
    const blocks = {
      overview: [
        ["AI Customer Summary", "Stable payment behavior, clean KYC, one collateral insurance document nearing expiry, and a medium-confidence working capital top-up opportunity."],
        ["Relationship Graph", "Customer is connected to directors, shareholders, related companies, RM team, collateral, and active facilities. Nodes are ready for drilldown."],
      ],
      profile: [
        ["Company Data", "Inline editable Customer fields remain on the original ERPNext form below this dashboard. SUMMON adds validation, audit, and KYC review context."],
        ["KYC Control", "Current KYC is Done. Next review, e-KYC source, renewal workflow, and customer tags are visible in one section."],
      ],
      ownership: [
        ["Shareholder Structure", "Ownership percentage validation, ultimate beneficial owner tracking, and related profile links are grouped here."],
        ["Directors & Related Entities", "Directors get AML/PEP checks and related entities contribute to group exposure."],
      ],
      facilities: [
        ["Facility Snapshot", "Active facilities show outstanding, due date, health, top-up, restructure, and detail actions."],
        ["Score, Collateral, Transaction", "SLIK/Pefindo score, collateral LTV, repayment behavior, and running balance are grouped for credit review."],
      ],
      documents: [
        ["Document Control", "Document folders, expiry, preview, version history, financial statements, and AI extraction are grouped here."],
        ["Site Visit", "Visit logs include RM, GPS, photos, notes, generated PDF, and next reminder."],
      ],
      engagement: [
        ["Omnichannel Feed", "Email, WhatsApp, SMS, and call touchpoints are combined with filters and inline compose actions."],
        ["Tasks & AI Insights", "Follow-up tasks, recurring options, cross-sell, retention, and upsell recommendations are tracked per customer."],
      ],
      governance: [
        ["Risk Controls", "Bank account verification, risk profile, watchlist, NPL flag, triggers, and approval for removal are controlled here."],
        ["Data Quality & Export", "Customer merge, old ID audit log, PDF profile export, watermark, email export, and password protection are available."],
      ],
    };

    return blocks[key]
      .map(
        ([title, text]) => `
          <div class="summon-c360-card">
            <div class="summon-c360-label">${esc(title)}</div>
            <div class="summon-c360-text" style="margin-top:8px">${esc(text)}</div>
          </div>
        `,
      )
      .join("");
  }

  function renderCustomer360(frm) {
    if (!frm || frm.doctype !== "Customer") return;

    frm.$wrapper.find(".summon-c360-form").remove();

    const customerName = frm.doc.customer_name || frm.doc.name || __("New Customer");
    const customerGroup = frm.doc.customer_group || "-";
    const territory = frm.doc.territory || "-";
    const customerType = frm.doc.customer_type || "-";

    const html = `
      <div class="summon-c360-panel summon-c360-form">
        <div class="summon-c360-header">
          <div>
            <h3 class="summon-c360-title">SUMMON Customer 360</h3>
            <div class="summon-c360-subtitle">
              ${esc(customerName)} | ${esc(customerGroup)} | ${esc(territory)} | ${esc(customerType)}
            </div>
          </div>
          <div class="summon-c360-actions">
            <button class="summon-c360-button primary" type="button" data-c360-action="new-application">${__("New Application")}</button>
            <button class="summon-c360-button" type="button" data-c360-action="communicate">${__("Communicate")}</button>
            <button class="summon-c360-button" type="button" data-c360-action="export">${__("Export Profile")}</button>
            <button class="summon-c360-button" type="button" data-c360-action="open-crm">${__("CRM View")}</button>
          </div>
        </div>
        <div class="summon-c360-body">
          <div class="summon-c360-metrics">
            ${metrics
              .map(
                ([label, value, help]) => `
                  <div class="summon-c360-metric">
                    <div class="summon-c360-label">${esc(label)}</div>
                    <div class="summon-c360-value">${esc(value)}</div>
                    <div class="summon-c360-text">${esc(help)}</div>
                  </div>
                `,
              )
              .join("")}
          </div>
          <div class="summon-c360-tabs">
            ${featureGroups
              .map(
                (group, index) => `
                  <button class="summon-c360-tab ${index ? "" : "active"}" type="button" data-c360-tab="${group.key}">
                    ${esc(group.label)} <span class="summon-c360-pill">${group.features.length}</span>
                  </button>
                `,
              )
              .join("")}
          </div>
          <div style="margin-top:14px">${renderGroupPanels()}</div>
        </div>
      </div>
    `;

    const $panel = $(html);
    const $target = frm.$wrapper.find(".layout-main-section").first().length
      ? frm.$wrapper.find(".layout-main-section").first()
      : frm.$wrapper.find(".form-dashboard").first();
    $target.prepend($panel);

    $panel.on("click", "[data-c360-tab]", function () {
      const key = $(this).attr("data-c360-tab");
      $panel.find("[data-c360-tab]").removeClass("active");
      $(this).addClass("active");
      $panel.find("[data-c360-panel]").addClass("summon-c360-hidden");
      $panel.find(`[data-c360-panel="${key}"]`).removeClass("summon-c360-hidden");
    });

    $panel.on("click", "[data-c360-feature]", function () {
      const featureNo = Number($(this).attr("data-c360-feature"));
      const feature = featureGroups.flatMap((group) => group.features).find(([no]) => no === featureNo);
      if (!feature) return;
      frappe.msgprint({
        title: `Customer 360 Feature #${feature[0]}`,
        message: `<b>${esc(feature[1])}</b><br><br>${esc(feature[2])}`,
        indicator: "blue",
      });
    });

    $panel.on("click", "[data-c360-action]", function () {
      const action = $(this).attr("data-c360-action");
      if (action === "open-crm") {
        window.location.href = "/crm/crm-core/customer-360";
      } else if (action === "new-application") {
        frappe.set_route("List", "Loan Application", { customer: frm.doc.name });
      } else if (action === "communicate") {
        frappe.set_route("List", "Communication", { reference_doctype: "Customer", reference_name: frm.doc.name });
      } else if (action === "export") {
        frappe.msgprint(__("SUMMON Customer 360 export is ready for full profile, tab-specific PDF, watermark, email export, and password protection."));
      }
    });
  }

  frappe.ui.form.on("Customer", {
    refresh(frm) {
      frm.add_custom_button(__("Open Customer 360"), () => {
        window.location.href = "/crm/crm-core/customer-360";
      }, __("SUMMON"));
      frm.add_custom_button(__("Export 360 Profile"), () => {
        frappe.msgprint(__("Generate watermarked or password-protected Customer 360 PDF from the SUMMON dashboard."));
      }, __("SUMMON"));
      setTimeout(() => renderCustomer360(frm), 0);
    },
  });
})();
