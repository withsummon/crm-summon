(function () {
  const baseSettings = frappe.listview_settings["Customer"] || {};

  const groups = [
    ["Overview", "Overview tab, AI summary, relationship graph, timeline, global search"],
    ["Profile & KYC", "Company data, KTP/NPWP validation, KYC status, customer tagging"],
    ["Ownership", "Shareholders, directors, AML/PEP, UBO, related entities, group exposure"],
    ["Facilities", "Financing history, active facilities, credit score, collateral, transactions"],
    ["Documents", "DMS folders, versions, expiry, financial statements, AI extraction, site visits"],
    ["Engagement", "Omnichannel communications, customer tasks, AI insights and outcomes"],
    ["Governance", "Bank accounts, risk profile, watchlist, merge, export profile"],
  ];

  function esc(value) {
    return $("<div>").text(value == null ? "" : String(value)).html();
  }

  function renderCustomer360List(listview) {
    if (!listview || !listview.page || !listview.page.main) return;

    const $main = listview.page.main.find(".layout-main-section").first().length
      ? listview.page.main.find(".layout-main-section").first()
      : listview.page.main;

    $main.find(".summon-c360-list").remove();

    const html = `
      <div class="summon-c360-panel summon-c360-list">
        <div class="summon-c360-body">
          <div class="summon-c360-list-summary">
            <div class="summon-c360-card">
              <div class="summon-c360-label">${__("Quick Metrics")}</div>
              <table class="summon-c360-table" style="margin-top:8px">
                <tbody>
                  <tr><td>Total Customers</td><td>${esc(listview.data?.length || 0)} loaded</td></tr>
                  <tr><td>Customer 360 Features</td><td>27 enabled</td></tr>
                  <tr><td>Primary Source</td><td>Selling &gt; Customer</td></tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    `;

    const $panel = $(html);
    $main.prepend($panel);

    $panel.on("click", "[data-c360-list-action]", function () {
      const action = $(this).attr("data-c360-list-action");
      if (action === "add") {
        frappe.new_doc("Customer");
      } else if (action === "refresh") {
        listview.refresh();
      } else if (action === "crm") {
        window.location.href = "/crm/crm-core/customer-360";
      }
    });
  }

  frappe.listview_settings["Customer"] = {
    ...baseSettings,
    add_fields: Array.from(
      new Set([
        ...(baseSettings.add_fields || []),
        "customer_name",
        "territory",
        "customer_group",
        "customer_type",
        "image",
      ]),
    ),
    onload(listview) {
      if (typeof baseSettings.onload === "function") {
        baseSettings.onload(listview);
      }
      listview.page.add_inner_button(__("Customer 360"), () => {
        window.location.href = "/crm/crm-core/customer-360";
      });
      setTimeout(() => renderCustomer360List(listview), 0);
    },
    refresh(listview) {
      if (typeof baseSettings.refresh === "function") {
        baseSettings.refresh(listview);
      }
      setTimeout(() => renderCustomer360List(listview), 0);
    },
  };
})();
