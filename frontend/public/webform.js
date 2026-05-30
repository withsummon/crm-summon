(function() {
  'use strict';

  var SCRIPT = document.currentScript || (function() {
    var scripts = document.getElementsByTagName('script');
    return scripts[scripts.length - 1];
  })();

  var BASE = SCRIPT.src.replace(/\/webform\.js.*/, '') || '';
  var TOKEN = (SCRIPT.src.split('?')[1] || '').replace(/^token=/, '') || '';
  var SLUG = (SCRIPT.getAttribute('data-slug') || '');

  if (!SLUG) {
    var m = SCRIPT.src.match(/[?&]slug=([^&]+)/);
    if (m) SLUG = decodeURIComponent(m[1]);
  }

  var CONTAINER_ID = 'summon-lead-form-' + SLUG;
  var container = document.getElementById(CONTAINER_ID);
  if (!container) {
    console.error('BNI CRM WebForm: container #' + CONTAINER_ID + ' not found');
    return;
  }

  function getParam(name) {
    var m = window.location.search.match(new RegExp('[?&]' + name + '=([^&]+)'));
    return m ? decodeURIComponent(m[1]) : '';
  }

  function api(method, args) {
    return new Promise(function(resolve, reject) {
      var xhr = new XMLHttpRequest();
      xhr.open('POST', BASE + '/api/method/' + method, true);
      xhr.setRequestHeader('Content-Type', 'application/json');
      xhr.onload = function() {
        if (xhr.status >= 200 && xhr.status < 300) {
          try { resolve(JSON.parse(xhr.responseText).message); } catch (e) { resolve({}); }
        } else {
          try { reject(JSON.parse(xhr.responseText)); } catch (e) { reject({ message: 'Request failed' }); }
        }
      };
      xhr.onerror = function() { reject({ message: 'Network error' }); };
      xhr.send(JSON.stringify(args));
    });
  }

  function renderForm(config) {
    var fields = config.fields || [];
    var html = '<form id="' + CONTAINER_ID + '-form" style="font-family:system-ui,-apple-system,sans-serif;max-width:420px;">'
      + '<div style="font-size:18px;font-weight:600;margin-bottom:12px;">' + escapeHtml(config.form_name || 'Get in touch') + '</div>';

    fields.forEach(function(f) {
      var type = f.fieldname === 'email' ? 'email' : (f.fieldname === 'annual_revenue' ? 'number' : 'text');
      html += '<div style="margin-bottom:10px;">'
        + '<label style="display:block;font-size:12px;color:#555;margin-bottom:4px;">' + escapeHtml(f.label) + (f.required ? ' *' : '') + '</label>'
        + '<input name="' + f.fieldname + '" type="' + type + '" ' + (f.required ? 'required' : '') + ' style="width:100%;padding:8px 10px;border:1px solid #ddd;border-radius:6px;font-size:14px;box-sizing:border-box;" />'
        + '</div>';
    });

    html += '<button type="submit" style="width:100%;padding:10px;background:#FF6600;color:#fff;border:none;border-radius:6px;font-size:14px;font-weight:600;cursor:pointer;">Submit</button>'
      + '<div id="' + CONTAINER_ID + '-error" style="color:#c00;font-size:12px;margin-top:8px;display:none;"></div>'
      + '</form>';

    container.innerHTML = html;

    var form = document.getElementById(CONTAINER_ID + '-form');
    var errorEl = document.getElementById(CONTAINER_ID + '-error');

    form.addEventListener('submit', function(e) {
      e.preventDefault();
      errorEl.style.display = 'none';
      var payload = {};
      fields.forEach(function(f) {
        var el = form.querySelector('[name="' + f.fieldname + '"]');
        if (el) payload[f.fieldname] = el.value;
      });
      var utm = {
        utm_source: getParam('utm_source'),
        utm_medium: getParam('utm_medium'),
        utm_campaign: getParam('utm_campaign'),
      };
      api('crm.api.lead_management.submit_webform', { form: SLUG, payload: payload, utm: utm })
        .then(function(res) {
          if (res.created) {
            window.location.href = config.redirect_url;
          } else if (res.duplicate) {
            errorEl.textContent = 'We already have your details. We will be in touch soon.';
            errorEl.style.display = 'block';
          } else {
            errorEl.textContent = 'Something went wrong. Please try again.';
            errorEl.style.display = 'block';
          }
        })
        .catch(function(err) {
          errorEl.textContent = (err.message || 'Submission failed.') + '';
          errorEl.style.display = 'block';
        });
    });
  }

  function escapeHtml(text) {
    var div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  api('crm.api.lead_management.get_webform_config', { form: SLUG })
    .then(renderForm)
    .catch(function(err) {
      container.innerHTML = '<div style="color:#c00;font-size:14px;">' + escapeHtml(err.message || 'Unable to load form.') + '</div>';
    });
})();
