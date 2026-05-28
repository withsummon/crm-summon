<template>
  <div class="flex h-full flex-col bg-slate-50 font-sans">
    <LayoutHeader stretch-left>
      <template #left-header>
        <div class="flex min-w-0 items-center gap-3">
          <div class="flex h-9 w-9 items-center justify-center rounded-[12px] bg-gradient-to-br from-teal-500 to-teal-700">
            <FeatherIcon name="file-text" class="h-4 w-4 text-white" />
          </div>
          <div class="min-w-0">
            <h1 class="truncate text-lg font-semibold text-ink-gray-9">{{ __('Loan Origination') }}</h1>
          </div>
        </div>
      </template>
      <template #right-header>
        <button @click="startNew" class="flex items-center gap-1.5 rounded-lg bg-teal-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-teal-700 transition-colors">
          <FeatherIcon name="plus" class="h-3.5 w-3.5" />
          {{ __('New Loan Application') }}
        </button>
      </template>
    </LayoutHeader>
    <div class="flex flex-1 min-h-0 overflow-hidden">
    <!-- Sidebar -->
    <div v-if="!isMobile || !selected" class="w-full md:w-72 border-r border-slate-200 bg-white flex flex-col shrink-0 h-full">
      <div class="px-4 py-2.5 border-b border-slate-200">
        <p class="text-xs text-slate-500">{{ filteredApps.length }} {{ __('applications') }}</p>
      </div>
      <div class="p-3 border-b border-slate-100">
        <div class="relative">
          <input v-model="searchQuery" type="text" :placeholder="__('Search...')" class="w-full pl-8 pr-3 py-1.5 bg-slate-100 rounded-lg text-xs focus:outline-none focus:ring-1 focus:ring-teal-500" />
          <FeatherIcon name="search" class="absolute left-2.5 top-2 h-3.5 w-3.5 text-slate-400" />
        </div>
      </div>
      <div class="flex-1 overflow-y-auto p-2 space-y-1">
        <div
          v-for="app in filteredApps" :key="app.id"
          @click="selectApp(app)"
          class="group p-3 rounded-lg cursor-pointer border transition-all"
          :class="selected?.id === app.id ? 'bg-teal-50 border-teal-200' : 'border-transparent hover:bg-slate-50'"
        >
          <div class="flex items-start justify-between gap-1">
            <span class="text-xs font-semibold text-slate-800 truncate">{{ app.borrower_name }}</span>
            <div class="flex items-center gap-1 shrink-0">
              <span class="rounded-full px-1.5 py-0.5 text-[9px] font-bold" :class="statusBadge(app.status)">{{ app.status }}</span>
              <button @click.stop="confirmDelete(app)" class="bg-red-50 transition-opacity p-0.5 rounded hover:bg-red-600 text-red-500 hover:text-gray-300">
                <FeatherIcon name="trash-2" class="h-3 w-3" />
              </button>
            </div>
          </div>
          <div class="text-[10px] text-slate-400 mt-0.5 truncate">{{ app.id }} · {{ app.facility_type }}</div>
          <div class="flex gap-0.5 mt-2">
            <div v-for="s in 8" :key="s" class="h-1 flex-1 rounded-full" :class="(app.step||1) >= s ? 'bg-teal-500' : 'bg-slate-200'" />
          </div>
          <div class="text-[9px] text-slate-400 mt-1">{{ STEPS[Math.min((app.step||1)-1,7)].short }}</div>
        </div>
      </div>
    </div>

    <!-- Main -->
    <div v-if="!isMobile || selected" class="flex-1 flex flex-col min-w-0 overflow-hidden h-full">
      <!-- Empty state -->
      <div v-if="!selected" class="flex-1 flex flex-col items-center justify-center p-8">
        <div class="w-16 h-16 rounded-full bg-teal-50 flex items-center justify-center mb-4">
          <FeatherIcon name="file-text" class="h-8 w-8 text-teal-300" />
        </div>
        <h3 class="text-base font-semibold text-slate-700">{{ __('Select an Application') }}</h3>
        <p class="text-sm text-slate-400 mt-1 text-center max-w-xs">{{ __('Or create a new loan application to start the origination process.') }}</p>
        <button @click="startNew" class="mt-4 flex items-center gap-2 rounded-lg bg-teal-600 px-4 py-2 text-sm font-semibold text-white hover:bg-teal-700 transition-colors">
          <FeatherIcon name="plus" class="h-4 w-4" />{{ __('New Loan Application') }}
        </button>
      </div>

      <template v-else>
        <!-- App Header -->
        <div class="bg-white border-b border-slate-200 px-5 py-3 flex items-center justify-between shrink-0 shadow-sm">
          <div class="flex items-center gap-3 min-w-0">
            <div class="w-10 h-10 rounded-xl bg-teal-600 text-white flex items-center justify-center font-black text-sm shrink-0 shadow-md shadow-teal-600/20">{{ initials(selected.borrower_name) }}</div>
            <div class="min-w-0">
              <div class="flex items-center gap-2">
                <h1 class="text-base font-bold text-slate-800 truncate">{{ selected.borrower_name }}</h1>
                <span class="text-[10px] rounded-full px-2 py-0.5 font-semibold" :class="selected.borrower_type==='Corporate' ? 'bg-purple-100 text-purple-700' : 'bg-teal-100 text-teal-700'">{{ selected.borrower_type }}</span>
              </div>
              <div class="text-xs text-slate-400 flex gap-2">
                <span class="font-mono">{{ selected.id }}</span>
                <span v-if="selected.facility_type">· {{ selected.facility_type }}</span>
                <span v-if="selected.requested_amount">· {{ fmt(selected.requested_amount) }}</span>
              </div>
            </div>
          </div>
          <div class="flex items-center gap-2 shrink-0">
            <button v-if="isMobile" @click="selected = null" class="rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-semibold text-slate-600 hover:bg-slate-50 transition-colors flex items-center gap-1 mr-1">
              <FeatherIcon name="chevron-left" class="h-4 w-4" />
              <span>{{ __('Queue') }}</span>
            </button>
            <span v-if="autoSaved" class="text-[10px] text-slate-400 flex items-center gap-1">
              <FeatherIcon name="check" class="h-3 w-3 text-teal-500" />{{ __('Auto-saved') }}
            </span>
            <button @click="prevStep" :disabled="currentStep===1" class="rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-semibold text-slate-600 hover:bg-slate-50 disabled:opacity-40 transition-colors">
              <FeatherIcon name="chevron-left" class="h-4 w-4" />
            </button>
            <button @click="nextStep" :disabled="currentStep===8" class="flex items-center gap-1.5 rounded-lg bg-teal-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-teal-700 disabled:opacity-40 transition-colors">
              <FeatherIcon v-if="saving" name="loader" class="h-3.5 w-3.5 animate-spin" />
              <span>{{ currentStep < 3 ? __('Save & Next') : __('Next') }}</span>
              <FeatherIcon v-if="!saving" name="chevron-right" class="h-3.5 w-3.5" />
            </button>
            <button v-if="currentStep===8" class="flex items-center gap-1.5 rounded-lg bg-green-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-green-700 transition-colors">
              <FeatherIcon name="check-circle" class="h-3.5 w-3.5" />{{ __('Complete') }}
            </button>
          </div>
        </div>

        <!-- Step Bar -->
        <div class="bg-white border-b border-slate-100 px-5 py-3 shrink-0 overflow-x-auto">
          <div class="flex items-start min-w-max gap-0">
            <div v-for="(step, idx) in STEPS" :key="step.id" class="flex items-center">
              <div class="flex flex-col items-center w-20 cursor-pointer" @click="jumpStep(step.id)">
                <div class="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold border-2 transition-all"
                  :class="currentStep>step.id ? 'bg-teal-600 border-teal-600 text-white' : currentStep===step.id ? 'bg-white border-teal-600 text-teal-600' : 'bg-white border-slate-300 text-slate-400'">
                  <FeatherIcon v-if="currentStep>step.id" name="check" class="h-3.5 w-3.5" />
                  <span v-else>{{ step.id }}</span>
                </div>
                <div class="text-center mt-1.5">
                  <div class="text-[10px] font-medium leading-tight" :class="currentStep===step.id ? 'text-teal-600 font-bold' : currentStep>step.id ? 'text-slate-500' : 'text-slate-400'">{{ step.short }}</div>
                  <div v-if="step.id <= 3" class="text-[8px] text-teal-400">backend</div>
                </div>
              </div>
              <div v-if="idx<7" class="w-6 h-0.5 mb-4 shrink-0" :class="currentStep>step.id ? 'bg-teal-500' : 'bg-slate-200'" />
            </div>
          </div>
        </div>

        <!-- Step Content -->
        <div class="flex-1 overflow-y-auto p-5 min-h-0">

          <!-- ── STEP 1: APPLICATION INTAKE ── -->
          <div v-if="currentStep===1" class="max-w-3xl mx-auto space-y-5">
            <StepHeader icon="edit-3" title="Application Intake" sub="Product selection, borrower profile, KYC & OCR" badge="Connects to Backend" />

            <!-- Product Selection -->
            <div class="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
              <h4 class="text-xs font-bold text-slate-700 mb-3 uppercase tracking-wide">{{ __('Product Selection') }}</h4>
              <div class="grid grid-cols-3 gap-3">
                <div v-for="prod in products" :key="prod.id"
                  @click="form.facility_type = prod.id"
                  class="rounded-xl border-2 p-3 cursor-pointer transition-all"
                  :class="form.facility_type===prod.id ? 'border-teal-500 bg-teal-50' : 'border-slate-200 hover:border-teal-300'">
                  <div class="w-8 h-8 rounded-lg flex items-center justify-center mb-2" :class="form.facility_type===prod.id ? 'bg-teal-100' : 'bg-slate-100'">
                    <FeatherIcon :name="prod.icon" class="h-4 w-4" :class="form.facility_type===prod.id ? 'text-teal-600' : 'text-slate-500'" />
                  </div>
                  <div class="text-xs font-semibold text-slate-800">{{ prod.name }}</div>
                  <div class="text-[10px] text-slate-400 mt-0.5">{{ prod.tenor }}</div>
                  <div v-if="form.facility_type===prod.id" class="mt-2 text-[9px] bg-teal-100 text-teal-700 rounded px-1.5 py-0.5 font-semibold w-fit">{{ __('Selected') }}</div>
                </div>
              </div>
            </div>

            <!-- Borrower Info -->
            <div class="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
              <h4 class="text-xs font-bold text-slate-700 mb-3 uppercase tracking-wide">{{ __('Borrower Information') }}</h4>
              <div class="grid grid-cols-2 gap-4">
                <div class="col-span-2">
                  <label class="field-label">{{ __('Full Name / Company Name') }} <span class="text-red-400">*</span></label>
                  <input v-model="form.borrower_name" type="text" :placeholder="__('e.g. PT Maju Bersama / Budi Santoso')" class="field-input" />
                </div>
                <div>
                  <label class="field-label">{{ __('Borrower Type') }}</label>
                  <select v-model="form.borrower_type" class="field-select">
                    <option value="Individual">Individual</option>
                    <option value="Corporate">Corporate / PT</option>
                    <option value="UMKM">UMKM / CV / UD</option>
                  </select>
                </div>
                <div>
                  <label class="field-label">{{ __('NPWP') }}</label>
                  <div class="relative">
                    <input v-model="form.npwp" type="text" placeholder="XX.XXX.XXX.X-XXX.XXX" class="field-input font-mono pr-16" />
                    <button @click="fakeNpwpValidate" class="absolute right-2 top-1.5 text-[10px] bg-teal-600 text-white px-2 py-0.5 rounded font-semibold">{{ npwpStatus || __('Validate') }}</button>
                  </div>
                </div>
                <div>
                  <label class="field-label">{{ __('Phone') }}</label>
                  <input v-model="form.phone" type="tel" placeholder="+62 8xx xxxx xxxx" class="field-input" />
                </div>
                <div>
                  <label class="field-label">{{ __('Email') }}</label>
                  <input v-model="form.email" type="email" placeholder="borrower@example.com" class="field-input" />
                </div>
                <div>
                  <label class="field-label">{{ __('Employer / Holding') }}</label>
                  <input v-model="form.employer_name" type="text" :placeholder="__('Company name')" class="field-input" />
                </div>
                <div>
                  <label class="field-label">{{ __('Industry (KBLI)') }}</label>
                  <select v-model="form.industry" class="field-select">
                    <option value="">{{ __('Select...') }}</option>
                    <option v-for="ind in industries" :key="ind">{{ ind }}</option>
                  </select>
                </div>
              </div>
            </div>

            <!-- KYC Status -->
            <div class="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
              <div class="flex items-center justify-between mb-3">
                <h4 class="text-xs font-bold text-slate-700 uppercase tracking-wide">{{ __('KYC Collection') }}</h4>
                <span class="text-[10px] bg-amber-100 text-amber-700 px-2 py-0.5 rounded-full font-semibold">AML/PEP Screening</span>
              </div>
              <div class="grid grid-cols-2 gap-3">
                <div v-for="kyc in kycItems" :key="kyc.id" class="flex items-center gap-3 p-3 rounded-lg border" :class="kyc.status==='Verified' ? 'bg-green-50 border-green-200' : kyc.status==='Pending' ? 'bg-amber-50 border-amber-200' : 'bg-slate-50 border-slate-200'">
                  <div class="w-7 h-7 rounded-full flex items-center justify-center shrink-0 cursor-pointer" :class="kyc.status==='Verified' ? 'bg-green-500' : kyc.status==='Pending' ? 'bg-amber-400' : 'bg-slate-300'" @click="cycleKyc(kyc)">
                    <FeatherIcon :name="kyc.status==='Verified' ? 'check' : 'clock'" class="h-3.5 w-3.5 text-white" />
                  </div>
                  <div class="flex-1 min-w-0">
                    <div class="text-xs font-semibold text-slate-800">{{ kyc.name }}</div>
                    <div class="text-[10px]" :class="kyc.status==='Verified' ? 'text-green-600' : kyc.status==='Pending' ? 'text-amber-600' : 'text-slate-400'">{{ kyc.status }}</div>
                  </div>
                  <button @click="fakeOcr(kyc)" v-if="kyc.ocr" class="text-[10px] text-teal-600 font-semibold hover:underline shrink-0">OCR</button>
                </div>
              </div>
              <!-- PEP/AML result -->
              <div class="mt-3 rounded-lg bg-green-50 border border-green-200 px-3 py-2 flex items-center gap-2">
                <FeatherIcon name="shield" class="h-4 w-4 text-green-500 shrink-0" />
                <span class="text-xs text-green-700 font-medium">{{ __('PEP/Sanction Screening: Clear — No matches found in OFAC, UN, local watchlist') }}</span>
              </div>
            </div>

            <!-- OCR Result (shown after OCR click) -->
            <div v-if="ocrResult" class="bg-white rounded-xl border border-teal-200 shadow-sm p-5">
              <div class="flex items-center gap-2 mb-3">
                <FeatherIcon name="cpu" class="h-4 w-4 text-teal-600" />
                <h4 class="text-xs font-bold text-teal-700 uppercase tracking-wide">{{ __('OCR Extraction Result') }}</h4>
                <span class="ml-auto text-[10px] bg-teal-100 text-teal-700 px-2 py-0.5 rounded-full font-semibold">Confidence: 94%</span>
              </div>
              <div class="grid grid-cols-2 gap-3">
                <div v-for="field in ocrResult" :key="field.key" class="rounded-lg bg-slate-50 border border-slate-200 p-2.5">
                  <div class="text-[10px] text-slate-400 font-semibold">{{ field.key }}</div>
                  <div class="text-xs font-bold text-slate-800 mt-0.5 flex items-center justify-between">
                    <span>{{ field.value }}</span>
                    <span class="text-[9px] rounded px-1 font-semibold" :class="field.conf >= 90 ? 'bg-green-100 text-green-600' : 'bg-amber-100 text-amber-600'">{{ field.conf }}%</span>
                  </div>
                </div>
              </div>
              <button @click="applyOcr" class="mt-3 w-full rounded-lg bg-teal-600 text-white text-xs font-semibold py-2 hover:bg-teal-700 transition-colors">{{ __('Apply to Form') }}</button>
            </div>
          </div>

          <!-- ── STEP 2: DOCUMENT COLLECTION ── -->
          <div v-if="currentStep===2" class="max-w-3xl mx-auto space-y-5">
            <StepHeader icon="paperclip" title="Document Collection" sub="Upload, checklist, expiry tracking & version control" badge="Connects to Backend" />

            <!-- Upload zone -->
            <div class="bg-white rounded-xl border-2 border-dashed border-slate-300 hover:border-teal-400 transition-colors p-8 text-center cursor-pointer" @click="fakeUpload" @dragover.prevent @drop.prevent="fakeUpload">
              <div class="w-12 h-12 rounded-full bg-teal-50 flex items-center justify-center mx-auto mb-3">
                <FeatherIcon name="upload-cloud" class="h-6 w-6 text-teal-400" />
              </div>
              <p class="text-sm font-semibold text-slate-700">{{ __('Drag & drop files here, or click to upload') }}</p>
              <p class="text-xs text-slate-400 mt-1">{{ __('PDF, JPG, PNG, XLSX, DOCX — max 25 MB per file') }}</p>
              <div v-if="uploadProgress" class="mt-4 max-w-xs mx-auto">
                <div class="flex justify-between text-xs text-slate-500 mb-1">
                  <span>{{ uploadingFile }}</span>
                  <span>{{ uploadProgress }}%</span>
                </div>
                <div class="h-1.5 bg-slate-100 rounded-full overflow-hidden">
                  <div class="h-full bg-teal-500 rounded-full transition-all duration-300" :style="{ width: uploadProgress + '%' }" />
                </div>
              </div>
            </div>

            <!-- Document checklist -->
            <div class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
              <div class="px-5 py-3 border-b border-slate-100 flex items-center justify-between">
                <h4 class="text-xs font-bold text-slate-700 uppercase tracking-wide">{{ __('Required Documents') }}</h4>
                <div class="flex gap-3 text-xs">
                  <span class="text-green-600 font-semibold">{{ docsReceived }} {{ __('Received') }}</span>
                  <span class="text-amber-500 font-semibold">{{ docsPending }} {{ __('Pending') }}</span>
                  <span class="text-red-500 font-semibold">{{ docsMissing }} {{ __('Missing') }}</span>
                </div>
              </div>
              <div class="divide-y divide-slate-100">
                <div v-for="doc in documents" :key="doc.id" class="flex items-center gap-3 px-5 py-3">
                  <div class="w-7 h-7 rounded-full flex items-center justify-center shrink-0 cursor-pointer transition-colors"
                    :class="doc.status==='Received' ? 'bg-green-500' : doc.status==='Missing' ? 'bg-red-400' : 'bg-slate-200'"
                    @click="cycleDoc(doc)">
                    <FeatherIcon :name="doc.status==='Received' ? 'check' : doc.status==='Missing' ? 'x' : 'minus'" class="h-3.5 w-3.5 text-white" />
                  </div>
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-2">
                      <span class="text-xs font-semibold text-slate-800">{{ doc.name }}</span>
                      <span v-if="doc.required" class="text-[9px] text-red-400 font-bold">REQ</span>
                      <span v-if="doc.expiry" class="text-[9px] bg-amber-100 text-amber-700 px-1.5 rounded font-semibold">Exp: {{ doc.expiry }}</span>
                    </div>
                    <div class="text-[10px] text-slate-400">{{ doc.description }}</div>
                  </div>
                  <div class="flex items-center gap-2 shrink-0">
                    <span v-if="doc.version" class="text-[9px] text-slate-400">v{{ doc.version }}</span>
                    <select v-model="doc.status" class="text-xs rounded border px-2 py-1 focus:outline-none focus:ring-1 focus:ring-teal-500"
                      :class="doc.status==='Received' ? 'border-green-200 text-green-700 bg-green-50' : doc.status==='Missing' ? 'border-red-200 text-red-600 bg-red-50' : 'border-slate-200 text-slate-600'">
                      <option>Pending</option><option>Received</option><option>Missing</option><option>Waived</option>
                    </select>
                  </div>
                </div>
              </div>
              <!-- Submit gate -->
              <div class="px-5 py-3 bg-slate-50 border-t border-slate-200 flex items-center gap-3">
                <FeatherIcon :name="docsMissing > 0 ? 'alert-triangle' : 'check-circle'" class="h-4 w-4 shrink-0" :class="docsMissing > 0 ? 'text-amber-500' : 'text-green-500'" />
                <span class="text-xs" :class="docsMissing > 0 ? 'text-amber-700' : 'text-green-700'">
                  {{ docsMissing > 0 ? `${docsMissing} mandatory document(s) missing — submission blocked` : 'All required documents received — ready to proceed' }}
                </span>
                <span class="ml-auto text-xs font-bold text-teal-600">{{ Math.round(docsReceived / documents.length * 100) }}% complete</span>
              </div>
            </div>

            <!-- Uploaded files -->
            <div v-if="uploadedFiles.length" class="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
              <h4 class="text-xs font-bold text-slate-700 uppercase tracking-wide mb-3">{{ __('Uploaded Files') }}</h4>
              <div class="space-y-2">
                <div v-for="file in uploadedFiles" :key="file.name" class="flex items-center gap-3 p-2.5 rounded-lg bg-slate-50 border border-slate-200">
                  <FeatherIcon name="file" class="h-4 w-4 text-teal-500 shrink-0" />
                  <div class="flex-1 min-w-0">
                    <div class="text-xs font-semibold text-slate-800 truncate">{{ file.name }}</div>
                    <div class="text-[10px] text-slate-400">{{ file.size }} · {{ file.uploaded }}</div>
                  </div>
                  <span class="text-[10px] bg-green-100 text-green-700 px-2 py-0.5 rounded-full font-semibold">{{ __('Scanned OK') }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- ── STEP 3: CREDIT ANALYSIS ── -->
          <div v-if="currentStep===3" class="max-w-4xl mx-auto space-y-5">
            <StepHeader icon="bar-chart-2" title="Credit Analysis" sub="Financial spreading, ratios, risk scoring & AI recommendation" badge="Connects to Backend" />

            <!-- Key Ratios -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div v-for="r in ratios" :key="r.label" class="bg-white rounded-xl border border-slate-200 shadow-sm p-4 text-center">
                <div class="text-xl font-black" :class="r.ok ? 'text-teal-600' : 'text-red-500'">{{ r.value }}</div>
                <div class="text-[10px] text-slate-500 mt-1">{{ r.label }}</div>
                <div class="text-[9px] mt-1 font-semibold" :class="r.ok ? 'text-green-600' : 'text-red-500'">{{ r.ok ? '✓ Pass' : '✗ Breach' }}</div>
              </div>
            </div>

            <!-- Financial Spreading -->
            <div class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
              <div class="px-5 py-3 border-b border-slate-100 flex items-center justify-between">
                <h4 class="text-xs font-bold text-slate-700 uppercase tracking-wide">{{ __('Financial Spreading') }}</h4>
                <div class="flex gap-2">
                  <button class="text-xs text-teal-600 font-semibold hover:underline">{{ __('AI Extract from PDF') }}</button>
                  <button class="text-xs text-slate-500 hover:text-slate-700">{{ __('Export Excel') }}</button>
                </div>
              </div>
              <div class="overflow-x-auto">
                <table class="w-full text-xs">
                  <thead class="bg-slate-50">
                    <tr>
                      <th class="px-4 py-2.5 text-left font-semibold text-slate-600 w-48">{{ __('Item') }}</th>
                      <th v-for="yr in ['FY2022','FY2023','FY2024']" :key="yr" class="px-4 py-2.5 text-right font-semibold text-slate-600">{{ yr }}</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-slate-100">
                    <tr v-for="row in spreadingRows" :key="row.label" :class="row.bold ? 'bg-teal-50 font-semibold' : 'hover:bg-slate-50'">
                      <td class="px-4 py-2 text-slate-700" :class="row.indent ? 'pl-7 text-slate-500' : ''">{{ row.label }}</td>
                      <td v-for="val in row.values" :key="val" class="px-4 py-2 text-right font-mono text-slate-800" :class="row.bold ? 'text-teal-700' : ''">{{ val }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- 5C + Risk Score -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
              <div class="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
                <h4 class="text-xs font-bold text-slate-700 uppercase tracking-wide mb-4">{{ __('5C Analysis') }}</h4>
                <div class="space-y-3">
                  <div v-for="c in fiveC" :key="c.label">
                    <div class="flex justify-between text-xs mb-1">
                      <span class="text-slate-700">{{ c.label }}</span>
                      <span class="font-bold" :class="c.score>=70 ? 'text-teal-600' : c.score>=50 ? 'text-amber-600' : 'text-red-500'">{{ c.score }}/100</span>
                    </div>
                    <div class="h-1.5 bg-slate-100 rounded-full overflow-hidden">
                      <div class="h-full rounded-full" :class="c.score>=70 ? 'bg-teal-500' : c.score>=50 ? 'bg-amber-400' : 'bg-red-400'" :style="{width: c.score+'%'}" />
                    </div>
                  </div>
                </div>
              </div>

              <div class="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
                <h4 class="text-xs font-bold text-slate-700 uppercase tracking-wide mb-4">{{ __('Risk Scoring') }}</h4>
                <div class="text-center mb-4">
                  <div class="text-5xl font-black text-teal-600">742</div>
                  <div class="text-sm font-bold text-slate-600 mt-1">{{ __('Grade') }}: B+</div>
                  <div class="text-xs text-slate-400">0 — 1000 scale</div>
                </div>
                <div class="grid grid-cols-3 gap-2 text-center text-[10px]">
                  <div class="rounded-lg bg-red-50 p-2"><div class="font-bold text-red-600">0–499</div><div class="text-slate-500">High Risk</div></div>
                  <div class="rounded-lg bg-amber-50 p-2"><div class="font-bold text-amber-600">500–699</div><div class="text-slate-500">Medium</div></div>
                  <div class="rounded-lg bg-teal-50 border border-teal-200 p-2"><div class="font-bold text-teal-600">700–1000</div><div class="text-slate-500">Low Risk ✓</div></div>
                </div>
              </div>
            </div>

            <!-- AI Recommendation -->
            <div class="bg-white rounded-xl border border-teal-200 shadow-sm p-5">
              <div class="flex items-center gap-2 mb-3">
                <div class="w-7 h-7 rounded-lg bg-teal-100 flex items-center justify-center">
                  <FeatherIcon name="cpu" class="h-4 w-4 text-teal-600" />
                </div>
                <h4 class="text-xs font-bold text-teal-700 uppercase tracking-wide">{{ __('AI Recommendation') }}</h4>
                <span class="ml-auto text-[10px] bg-teal-100 text-teal-700 px-2 py-0.5 rounded-full font-semibold">Confidence: 87%</span>
              </div>
              <div class="flex gap-3 mb-3">
                <div v-for="rec in ['Approve','Refer','Reject']" :key="rec"
                  :class="rec==='Approve' ? 'bg-green-100 border-green-400 text-green-700 font-bold ring-2 ring-green-200' : 'bg-slate-50 border-slate-200 text-slate-400'"
                  class="flex-1 text-center rounded-xl border py-3 text-sm font-semibold cursor-pointer">
                  {{ rec }}
                </div>
              </div>
              <div class="rounded-lg bg-slate-50 border border-slate-200 p-3 text-xs text-slate-700 leading-relaxed">
                {{ __('Based on financial analysis, the borrower demonstrates adequate debt service capacity with DSCR of 1.42x (threshold: 1.2x). Risk score of 742 falls in low-risk band. Recommend approval subject to: (1) NPWP validation, (2) collateral appraisal completion, (3) net worth confirmation via SLIK report.') }}
              </div>
              <div class="mt-3">
                <label class="field-label">{{ __('Analyst Notes') }}</label>
                <textarea v-model="form.analyst_notes" rows="3" :placeholder="__('Add analyst commentary...')" class="field-input resize-none" />
              </div>
            </div>
          </div>

          <!-- ── STEP 4: COLLATERAL MANAGEMENT ── -->
          <div v-if="currentStep===4" class="max-w-3xl mx-auto space-y-5">
            <StepHeader icon="shield" title="Collateral Management" sub="Registration, appraisal, insurance & legal documents" />

            <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div v-for="c in collaterals" :key="c.id" class="bg-white rounded-xl border border-slate-200 shadow-sm p-4">
                <div class="flex items-start justify-between mb-3">
                  <div class="w-8 h-8 rounded-lg bg-teal-100 flex items-center justify-center">
                    <FeatherIcon :name="c.icon" class="h-4 w-4 text-teal-600" />
                  </div>
                  <span class="text-[10px] rounded-full px-2 py-0.5 font-semibold" :class="c.status==='Appraised' ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'">{{ c.status }}</span>
                </div>
                <div class="text-sm font-bold text-slate-800">{{ c.name }}</div>
                <div class="text-[10px] text-slate-500 mt-0.5">{{ c.id }}</div>
                <div class="mt-3 space-y-1.5 text-xs">
                  <div class="flex justify-between"><span class="text-slate-500">Market Value</span><span class="font-bold text-slate-800">{{ fmt(c.value) }}</span></div>
                  <div class="flex justify-between"><span class="text-slate-500">LTV</span><span class="font-bold" :class="c.ltv <= 80 ? 'text-teal-600' : 'text-red-500'">{{ c.ltv }}%</span></div>
                  <div class="flex justify-between"><span class="text-slate-500">Insured Until</span><span class="font-semibold text-slate-700">{{ c.insured }}</span></div>
                </div>
                <div class="mt-3 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                  <div class="h-full rounded-full" :class="c.ltv<=70 ? 'bg-teal-500' : c.ltv<=80 ? 'bg-amber-400' : 'bg-red-400'" :style="{width: c.ltv+'%'}" />
                </div>
              </div>
            </div>

            <!-- Appraisal -->
            <div class="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
              <h4 class="text-xs font-bold text-slate-700 uppercase tracking-wide mb-3">{{ __('Appraisal Management') }}</h4>
              <div class="overflow-x-auto">
                <table class="w-full text-xs">
                  <thead class="bg-slate-50">
                    <tr>
                      <th class="px-3 py-2 text-left text-slate-600">{{ __('Collateral') }}</th>
                      <th class="px-3 py-2 text-left text-slate-600">{{ __('Appraiser') }}</th>
                      <th class="px-3 py-2 text-right text-slate-600">{{ __('Value') }}</th>
                      <th class="px-3 py-2 text-center text-slate-600">{{ __('Date') }}</th>
                      <th class="px-3 py-2 text-center text-slate-600">{{ __('Next Re-appraisal') }}</th>
                      <th class="px-3 py-2 text-center text-slate-600">{{ __('Status') }}</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-slate-100">
                    <tr v-for="a in appraisals" :key="a.col" class="hover:bg-slate-50">
                      <td class="px-3 py-2 font-semibold text-slate-800">{{ a.col }}</td>
                      <td class="px-3 py-2 text-slate-600">{{ a.appraiser }}</td>
                      <td class="px-3 py-2 text-right font-mono font-bold text-teal-700">{{ fmt(a.value) }}</td>
                      <td class="px-3 py-2 text-center text-slate-500">{{ a.date }}</td>
                      <td class="px-3 py-2 text-center text-slate-500">{{ a.next }}</td>
                      <td class="px-3 py-2 text-center"><span class="rounded-full px-2 py-0.5 text-[9px] font-semibold" :class="a.status==='Completed' ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'">{{ a.status }}</span></td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- ── STEP 5: APPROVAL WORKFLOW ── -->
          <div v-if="currentStep===5" class="max-w-3xl mx-auto space-y-5">
            <StepHeader icon="check-circle" title="Approval Workflow" sub="Multi-level approval, committee routing & voting" />

            <!-- Approval Chain -->
            <div class="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
              <h4 class="text-xs font-bold text-slate-700 uppercase tracking-wide mb-4">{{ __('Approval Chain') }}</h4>
              <div class="flex flex-col gap-0">
                <div v-for="(lvl, idx) in approvalLevels" :key="lvl.id" class="flex items-start gap-4">
                  <div class="flex flex-col items-center">
                    <div class="w-8 h-8 rounded-full flex items-center justify-center border-2 text-xs font-bold shrink-0"
                      :class="lvl.state==='Approved' ? 'bg-teal-600 border-teal-600 text-white' : lvl.state==='Pending' ? 'bg-white border-teal-500 text-teal-600' : 'bg-white border-slate-300 text-slate-400'">
                      <FeatherIcon v-if="lvl.state==='Approved'" name="check" class="h-4 w-4" />
                      <span v-else>{{ lvl.id }}</span>
                    </div>
                    <div v-if="idx<approvalLevels.length-1" class="w-0.5 h-10 mt-1" :class="lvl.state==='Approved' ? 'bg-teal-400' : 'bg-slate-200'" />
                  </div>
                  <div class="flex-1 pb-4">
                    <div class="flex items-center justify-between gap-2">
                      <div>
                        <div class="text-sm font-bold text-slate-800">{{ lvl.approver }}</div>
                        <div class="text-xs text-slate-500">{{ lvl.role }}</div>
                      </div>
                      <div class="text-right shrink-0">
                        <span class="rounded-full px-2 py-0.5 text-[10px] font-semibold" :class="lvl.state==='Approved' ? 'bg-green-100 text-green-700' : lvl.state==='Pending' ? 'bg-amber-100 text-amber-700' : 'bg-slate-100 text-slate-500'">{{ lvl.state }}</span>
                        <div v-if="lvl.date" class="text-[10px] text-slate-400 mt-0.5">{{ lvl.date }}</div>
                      </div>
                    </div>
                    <div v-if="lvl.note" class="mt-1.5 text-xs text-slate-600 bg-slate-50 rounded-lg p-2 border border-slate-200 italic">"{{ lvl.note }}"</div>
                    <!-- SLA timer -->
                    <div v-if="lvl.state==='Pending'" class="mt-2 flex items-center gap-2">
                      <div class="flex-1 h-1 bg-slate-100 rounded-full overflow-hidden">
                        <div class="h-full bg-amber-400 rounded-full" style="width: 60%" />
                      </div>
                      <span class="text-[10px] text-amber-600 font-semibold">SLA: 14h remaining</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Committee Voting -->
            <div class="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
              <h4 class="text-xs font-bold text-slate-700 uppercase tracking-wide mb-3">{{ __('Committee Voting') }}</h4>
              <div class="grid grid-cols-2 gap-3 mb-4">
                <div v-for="m in committeeMembers" :key="m.name" class="flex items-center gap-2 p-3 rounded-lg border" :class="m.vote ? 'bg-teal-50 border-teal-200' : 'bg-slate-50 border-slate-200'">
                  <div class="w-8 h-8 rounded-full text-white flex items-center justify-center text-xs font-black shrink-0" :class="m.vote==='Approve' ? 'bg-teal-600' : m.vote==='Reject' ? 'bg-red-500' : 'bg-slate-400'">{{ m.name[0] }}</div>
                  <div class="flex-1 min-w-0">
                    <div class="text-xs font-semibold text-slate-800">{{ m.name }}</div>
                    <div class="text-[10px] text-slate-500">{{ m.role }}</div>
                  </div>
                  <span class="text-[10px] font-bold shrink-0" :class="m.vote==='Approve' ? 'text-teal-600' : m.vote==='Reject' ? 'text-red-500' : 'text-slate-400'">{{ m.vote || 'Pending' }}</span>
                </div>
              </div>
              <!-- Quorum -->
              <div class="rounded-lg bg-teal-50 border border-teal-200 px-4 py-3 flex items-center gap-3">
                <FeatherIcon name="check-circle" class="h-4 w-4 text-teal-600 shrink-0" />
                <div class="text-xs text-teal-700">
                  <span class="font-bold">Quorum met</span> — 3/4 voted · Majority: <span class="font-bold">Approved (3-0-1)</span>
                </div>
              </div>
            </div>
          </div>

          <!-- ── STEP 6: LEGAL & DOCUMENTATION ── -->
          <div v-if="currentStep===6" class="max-w-3xl mx-auto space-y-5">
            <StepHeader icon="file-text" title="Legal & Documentation" sub="Agreement generation, e-signing & covenant setup" />

            <!-- Agreements -->
            <div class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
              <div class="px-5 py-3 border-b border-slate-100 flex items-center justify-between">
                <h4 class="text-xs font-bold text-slate-700 uppercase tracking-wide">{{ __('Agreements') }}</h4>
                <button class="text-xs bg-teal-600 text-white px-3 py-1.5 rounded-lg font-semibold hover:bg-teal-700 transition-colors">{{ __('Generate from Template') }}</button>
              </div>
              <div class="divide-y divide-slate-100">
                <div v-for="ag in agreements" :key="ag.id" class="flex items-center gap-3 px-5 py-3">
                  <FeatherIcon name="file-text" class="h-4 w-4 text-teal-500 shrink-0" />
                  <div class="flex-1 min-w-0">
                    <div class="text-xs font-semibold text-slate-800">{{ ag.name }}</div>
                    <div class="text-[10px] text-slate-400">{{ ag.version }} · {{ ag.date }}</div>
                  </div>
                  <span class="text-[10px] rounded-full px-2 py-0.5 font-semibold" :class="ag.status==='Signed' ? 'bg-green-100 text-green-700' : ag.status==='Pending Signature' ? 'bg-amber-100 text-amber-700' : 'bg-slate-100 text-slate-600'">{{ ag.status }}</span>
                  <button class="text-[10px] text-teal-600 hover:underline font-semibold ml-2">{{ ag.status==='Draft' ? 'Review' : 'View' }}</button>
                </div>
              </div>
            </div>

            <!-- E-Sign -->
            <div class="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
              <h4 class="text-xs font-bold text-slate-700 uppercase tracking-wide mb-3">{{ __('Digital Signing (e-Sign)') }}</h4>
              <div class="grid grid-cols-3 gap-3 mb-3">
                <div v-for="sg in signers" :key="sg.name" class="rounded-xl border p-3 text-center" :class="sg.signed ? 'border-teal-200 bg-teal-50' : 'border-slate-200'">
                  <div class="w-8 h-8 rounded-full bg-teal-600 text-white flex items-center justify-center text-xs font-black mx-auto mb-2">{{ sg.name[0] }}</div>
                  <div class="text-xs font-semibold text-slate-800">{{ sg.name }}</div>
                  <div class="text-[10px] text-slate-400">{{ sg.role }}</div>
                  <div class="mt-2 text-[10px] font-bold" :class="sg.signed ? 'text-teal-600' : 'text-slate-400'">{{ sg.signed ? '✓ Signed' : 'Awaiting' }}</div>
                  <div v-if="sg.signed" class="text-[9px] text-slate-400">{{ sg.signed_at }}</div>
                </div>
              </div>
              <div class="rounded-lg bg-slate-50 border border-slate-200 px-3 py-2 text-[10px] text-slate-500">
                {{ __('Provider: Privy.id / Tilaka — UU ITE compliant — audit trail stored immutably') }}
              </div>
            </div>

            <!-- Covenants -->
            <div class="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
              <h4 class="text-xs font-bold text-slate-700 uppercase tracking-wide mb-3">{{ __('Covenant Setup') }}</h4>
              <div class="space-y-2">
                <div v-for="cov in covenants" :key="cov.id" class="flex items-center gap-3 p-3 rounded-lg bg-slate-50 border border-slate-200">
                  <div class="w-2 h-2 rounded-full shrink-0" :class="cov.type==='Financial' ? 'bg-teal-500' : 'bg-purple-400'" />
                  <div class="flex-1 min-w-0">
                    <div class="text-xs font-semibold text-slate-800">{{ cov.name }}</div>
                    <div class="text-[10px] text-slate-400">{{ cov.type }} · Tested {{ cov.frequency }}</div>
                  </div>
                  <div class="text-xs text-right shrink-0">
                    <div class="font-bold text-slate-800">Threshold: {{ cov.threshold }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- ── STEP 7: DISBURSEMENT ── -->
          <div v-if="currentStep===7" class="max-w-3xl mx-auto space-y-5">
            <StepHeader icon="send" title="Disbursement" sub="Verification checklist, tranche planning & payment instructions" />

            <!-- CP Checklist -->
            <div class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
              <div class="px-5 py-3 border-b border-slate-100">
                <h4 class="text-xs font-bold text-slate-700 uppercase tracking-wide">{{ __('Condition Precedent Checklist') }}</h4>
              </div>
              <div class="divide-y divide-slate-100">
                <div v-for="cp in cpItems" :key="cp.id" class="flex items-center gap-3 px-5 py-3">
                  <div class="w-6 h-6 rounded-full flex items-center justify-center shrink-0" :class="cp.cleared ? 'bg-teal-500' : 'bg-slate-200'">
                    <FeatherIcon :name="cp.cleared ? 'check' : 'minus'" class="h-3 w-3 text-white" />
                  </div>
                  <div class="flex-1 text-xs font-medium text-slate-800">{{ cp.name }}</div>
                  <span class="text-[10px] font-semibold" :class="cp.cleared ? 'text-teal-600' : 'text-slate-400'">{{ cp.cleared ? 'Cleared' : 'Open' }}</span>
                </div>
              </div>
              <div class="px-5 py-3 bg-slate-50 border-t border-slate-200">
                <div class="flex items-center gap-2">
                  <FeatherIcon :name="cpItems.every(c=>c.cleared) ? 'check-circle' : 'alert-triangle'" class="h-4 w-4 shrink-0" :class="cpItems.every(c=>c.cleared) ? 'text-teal-500' : 'text-amber-500'" />
                  <span class="text-xs font-semibold" :class="cpItems.every(c=>c.cleared) ? 'text-teal-700' : 'text-amber-700'">
                    {{ cpItems.filter(c=>c.cleared).length }}/{{ cpItems.length }} {{ __('conditions cleared') }}
                    {{ cpItems.every(c=>c.cleared) ? '— Disbursement authorized' : '— Block active' }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Tranches -->
            <div class="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
              <h4 class="text-xs font-bold text-slate-700 uppercase tracking-wide mb-3">{{ __('Disbursement Tranches') }}</h4>
              <div class="space-y-2">
                <div v-for="t in tranches" :key="t.id" class="flex items-center gap-3 p-3 rounded-lg border" :class="t.status==='Disbursed' ? 'bg-teal-50 border-teal-200' : t.status==='Pending' ? 'bg-amber-50 border-amber-200' : 'border-slate-200'">
                  <div class="w-8 h-8 rounded-lg flex items-center justify-center text-xs font-black shrink-0" :class="t.status==='Disbursed' ? 'bg-teal-100 text-teal-700' : 'bg-slate-100 text-slate-500'">{{ t.id }}</div>
                  <div class="flex-1 min-w-0">
                    <div class="text-xs font-semibold text-slate-800">Tranche {{ t.id }} — {{ fmt(t.amount) }}</div>
                    <div class="text-[10px] text-slate-400">{{ t.date }} · {{ t.condition }}</div>
                  </div>
                  <span class="text-[10px] rounded-full px-2 py-0.5 font-semibold shrink-0" :class="t.status==='Disbursed' ? 'bg-teal-100 text-teal-700' : 'bg-amber-100 text-amber-700'">{{ t.status }}</span>
                </div>
              </div>
            </div>

            <!-- Account Info -->
            <div class="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
              <h4 class="text-xs font-bold text-slate-700 uppercase tracking-wide mb-3">{{ __('Payment Instructions') }}</h4>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="field-label">{{ __('Bank') }}</label>
                  <select v-model="form.disbursement_bank" class="field-select">
                    <option value="">{{ __('Select bank...') }}</option>
                    <option v-for="b in ['BCA','Mandiri','BRI','BNI','CIMB Niaga','BSI']" :key="b">{{ b }}</option>
                  </select>
                </div>
                <div>
                  <label class="field-label">{{ __('Account Number') }}</label>
                  <input v-model="form.disbursement_account" type="text" placeholder="XXXX XXXX XXXX" class="field-input font-mono" />
                </div>
                <div>
                  <label class="field-label">{{ __('Account Holder') }}</label>
                  <input v-model="form.disbursement_holder" type="text" :placeholder="form.borrower_name" class="field-input" />
                </div>
                <div>
                  <label class="field-label">{{ __('Disbursement Date') }}</label>
                  <input v-model="form.disbursement_date" type="date" class="field-input" />
                </div>
              </div>
            </div>
          </div>

          <!-- ── STEP 8: POST-DISBURSEMENT ── -->
          <div v-if="currentStep===8" class="max-w-4xl mx-auto space-y-5">
            <StepHeader icon="activity" title="Post-Disbursement" sub="Health monitoring, payment tracking & covenant testing" />

            <!-- Health KPIs -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div v-for="kpi in healthKpis" :key="kpi.label" class="bg-white rounded-xl border border-slate-200 shadow-sm p-4 text-center">
                <div class="text-xl font-black" :class="kpi.color">{{ kpi.value }}</div>
                <div class="text-[10px] text-slate-500 mt-1">{{ kpi.label }}</div>
                <div class="mt-2 w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
                  <div class="h-full rounded-full" :class="kpi.barColor" :style="{width: kpi.pct+'%'}" />
                </div>
              </div>
            </div>

            <!-- Payment Schedule -->
            <div class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
              <div class="px-5 py-3 border-b border-slate-100 flex items-center justify-between">
                <h4 class="text-xs font-bold text-slate-700 uppercase tracking-wide">{{ __('Payment Tracking') }}</h4>
                <span class="text-[10px] text-slate-500">{{ __('Showing latest 6 installments') }}</span>
              </div>
              <div class="overflow-x-auto">
                <table class="w-full text-xs">
                  <thead class="bg-slate-50">
                    <tr>
                      <th class="px-4 py-2.5 text-left text-slate-600">#</th>
                      <th class="px-4 py-2.5 text-left text-slate-600">{{ __('Due Date') }}</th>
                      <th class="px-4 py-2.5 text-right text-slate-600">{{ __('Scheduled') }}</th>
                      <th class="px-4 py-2.5 text-right text-slate-600">{{ __('Actual Paid') }}</th>
                      <th class="px-4 py-2.5 text-right text-slate-600">{{ __('Outstanding') }}</th>
                      <th class="px-4 py-2.5 text-center text-slate-600">{{ __('Status') }}</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-slate-100">
                    <tr v-for="p in paymentRows" :key="p.n" class="hover:bg-slate-50">
                      <td class="px-4 py-2.5 text-slate-500">{{ p.n }}</td>
                      <td class="px-4 py-2.5 text-slate-700">{{ p.due }}</td>
                      <td class="px-4 py-2.5 text-right font-mono text-slate-700">{{ fmt(p.scheduled) }}</td>
                      <td class="px-4 py-2.5 text-right font-mono" :class="p.paid ? 'text-teal-700 font-semibold' : 'text-slate-400'">{{ p.paid ? fmt(p.paid) : '—' }}</td>
                      <td class="px-4 py-2.5 text-right font-mono text-slate-600">{{ fmt(p.outstanding) }}</td>
                      <td class="px-4 py-2.5 text-center">
                        <span class="rounded-full px-2 py-0.5 text-[9px] font-bold" :class="p.status==='Paid' ? 'bg-green-100 text-green-700' : p.status==='Overdue' ? 'bg-red-100 text-red-600' : 'bg-amber-100 text-amber-700'">{{ p.status }}</span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- Covenant Monitoring -->
            <div class="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
              <h4 class="text-xs font-bold text-slate-700 uppercase tracking-wide mb-3">{{ __('Covenant Monitoring') }}</h4>
              <div class="space-y-3">
                <div v-for="cov in covenantMonitoring" :key="cov.id">
                  <div class="flex items-center justify-between mb-1.5">
                    <div>
                      <span class="text-xs font-semibold text-slate-800">{{ cov.name }}</span>
                      <span class="ml-2 text-[10px] text-slate-400">Threshold: {{ cov.threshold }}</span>
                    </div>
                    <div class="flex items-center gap-2">
                      <span class="text-xs font-black" :class="cov.ok ? 'text-teal-600' : 'text-red-500'">{{ cov.actual }}</span>
                      <span class="text-[10px] rounded-full px-2 py-0.5 font-semibold" :class="cov.ok ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-600'">{{ cov.ok ? 'Pass' : 'Breach' }}</span>
                    </div>
                  </div>
                  <div class="h-2 bg-slate-100 rounded-full overflow-hidden">
                    <div class="h-full rounded-full transition-all" :class="cov.ok ? 'bg-teal-500' : 'bg-red-400'" :style="{width: Math.min(cov.pct, 100)+'%'}" />
                  </div>
                </div>
              </div>
            </div>
          </div>

        </div>
      </template>
    </div>
    </div>

    <!-- New Application Modal -->
    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm" @click.self="showModal=false">
      <div class="w-full max-w-sm bg-white rounded-2xl shadow-2xl p-6">
        <div class="flex items-center justify-between mb-5">
          <h3 class="text-base font-bold text-slate-800">{{ __('New Loan Application') }}</h3>
          <button @click="showModal=false" class="text-slate-400 hover:text-slate-600"><FeatherIcon name="x" class="h-5 w-5" /></button>
        </div>
        <div class="space-y-3">
          <div>
            <label class="field-label">{{ __('Borrower Name') }} <span class="text-red-400">*</span></label>
            <input v-model="newApp.borrower_name" type="text" :placeholder="__('Full name or company')" class="field-input" @keyup.enter="createApp" />
          </div>
          <div>
            <label class="field-label">{{ __('Type') }}</label>
            <select v-model="newApp.borrower_type" class="field-select">
              <option value="Individual">Individual</option>
              <option value="Corporate">Corporate / PT</option>
              <option value="UMKM">UMKM</option>
            </select>
          </div>
        </div>
        <div class="mt-5 flex gap-2">
          <button @click="showModal=false" class="flex-1 rounded-lg border border-slate-200 py-2 text-sm font-semibold text-slate-600 hover:bg-slate-50">{{ __('Cancel') }}</button>
          <button @click="createApp" :disabled="!newApp.borrower_name" class="flex-1 rounded-lg bg-teal-600 py-2 text-sm font-semibold text-white hover:bg-teal-700 disabled:opacity-50 transition-colors">{{ __('Create') }}</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Delete Confirmation Modal -->
  <div v-if="deleteTarget" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm" @click.self="deleteTarget = null">
    <div class="w-full max-w-sm bg-white rounded-2xl shadow-2xl p-6">
      <div class="flex items-center gap-3 mb-4">
        <div class="w-10 h-10 rounded-full bg-red-100 flex items-center justify-center shrink-0">
          <FeatherIcon name="trash-2" class="h-5 w-5 text-red-500" />
        </div>
        <div>
          <h3 class="text-base font-bold text-gray-800">{{ __('Delete Application') }}</h3>
          <p class="text-xs text-gray-500 mt-0.5">{{ __('This action cannot be undone.') }}</p>
        </div>
      </div>
      <div class="rounded-lg bg-gray-50 border border-gray-200 px-4 py-3 mb-5">
        <p class="text-xs font-semibold text-gray-800">{{ deleteTarget?.borrower_name }}</p>
        <p class="text-[10px] text-gray-400 mt-0.5">{{ deleteTarget?.id }} · {{ deleteTarget?.facility_type || 'No facility selected' }}</p>
      </div>
      <div class="flex gap-2">
        <button @click="deleteTarget = null" class="flex-1 rounded-lg border border-gray-200 py-2 text-sm font-semibold text-gray-600 hover:bg-gray-50">{{ __('Cancel') }}</button>
        <button @click="deleteApp" class="flex-1 rounded-lg bg-red-500 py-2 text-sm font-semibold text-white hover:bg-red-600 transition-colors">{{ __('Delete') }}</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, defineComponent, h } from 'vue'
import { FeatherIcon, call } from 'frappe-ui'
import LayoutHeader from '@/components/LayoutHeader.vue'

// ── Step Header helper component ──
const StepHeader = defineComponent({
  props: { icon: String, title: String, sub: String, badge: String },
  setup(props) {
    return () => h('div', { class: 'flex items-center gap-3' }, [
      h('div', { class: 'w-9 h-9 rounded-xl bg-teal-100 flex items-center justify-center shrink-0' },
        [h(FeatherIcon, { name: props.icon, class: 'h-5 w-5 text-teal-600' })]),
      h('div', { class: 'flex-1' }, [
        h('h3', { class: 'text-base font-bold text-slate-800' }, props.title),
        h('p', { class: 'text-xs text-slate-500' }, props.sub),
      ]),
      props.badge ? h('span', { class: 'text-[10px] bg-teal-100 text-teal-700 px-2 py-0.5 rounded-full font-semibold' }, props.badge) : null,
    ])
  },
})

// ── Constants ──
const STEPS = [
  { id: 1, short: 'Intake' },
  { id: 2, short: 'Documents' },
  { id: 3, short: 'Credit' },
  { id: 4, short: 'Collateral' },
  { id: 5, short: 'Approval' },
  { id: 6, short: 'Legal' },
  { id: 7, short: 'Disburse' },
  { id: 8, short: 'Post-Disb' },
]

const DEMO_APPS = [
  { id: 'LOS-2026-001', borrower_name: 'PT Maju Bersama Tbk', borrower_type: 'Corporate', step: 5, status: 'Committee', facility_type: 'Working Capital', requested_amount: 12500000000 },
  { id: 'LOS-2026-002', borrower_name: 'Budi Santoso', borrower_type: 'Individual', step: 2, status: 'Document Collection', facility_type: 'KPR', requested_amount: 850000000 },
  { id: 'LOS-2026-003', borrower_name: 'CV Teknik Jaya Mandiri', borrower_type: 'UMKM', step: 8, status: 'Active', facility_type: 'Investment Loan', requested_amount: 3200000000 },
  { id: 'LOS-2026-004', borrower_name: 'Siti Rahmawati', borrower_type: 'Individual', step: 3, status: 'Credit Analysis', facility_type: 'Multiguna', requested_amount: 200000000 },
]

// ── State ──
const apps = ref([...DEMO_APPS])
const selected = ref(null)
const currentStep = ref(1)
const searchQuery = ref('')
const saving = ref(false)
const autoSaved = ref(false)
const showModal = ref(false)
const newApp = ref({ borrower_name: '', borrower_type: 'Individual' })
const deleteTarget = ref(null)
const npwpStatus = ref('')
const ocrResult = ref(null)
const uploadProgress = ref(0)
const uploadingFile = ref('')
const isMobile = ref(false)
const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
}

const form = ref({
  borrower_name: '', borrower_type: 'Individual', npwp: '', phone: '', email: '',
  employer_name: '', industry: '', facility_type: '',
  requested_amount: 0, tenor_months: null, interest_rate: null,
  purpose: '', analyst_notes: '', disbursement_bank: '',
  disbursement_account: '', disbursement_holder: '', disbursement_date: '',
})

// ── Static data ──
const products = [
  { id: 'Working Capital', name: 'Working Capital', icon: 'trending-up', tenor: 'Up to 36 months' },
  { id: 'Investment Loan', name: 'Investment Loan', icon: 'tool', tenor: 'Up to 120 months' },
  { id: 'KPR', name: 'KPR', icon: 'home', tenor: 'Up to 240 months' },
  { id: 'KKB', name: 'KKB', icon: 'truck', tenor: 'Up to 60 months' },
  { id: 'Multiguna', name: 'Multiguna', icon: 'layers', tenor: 'Up to 60 months' },
  { id: 'Microfinance', name: 'KUR / Mikro', icon: 'dollar-sign', tenor: 'Up to 36 months' },
]

const industries = ['Manufacturing','Retail & FMCG','Financial Services','Real Estate','Agriculture','Construction','Technology','Healthcare','Transportation']

const kycItems = ref([
  { id: 1, name: 'KTP / Passport', status: 'Verified', ocr: true },
  { id: 2, name: 'NPWP', status: 'Pending', ocr: true },
  { id: 3, name: 'Kartu Keluarga', status: 'Verified', ocr: false },
  { id: 4, name: 'Beneficial Owner Declaration', status: 'Not Submitted', ocr: false },
  { id: 5, name: 'SIUP / NIB', status: 'Verified', ocr: false },
  { id: 6, name: 'Akta Pendirian', status: 'Pending', ocr: false },
])

const documents = ref([
  { id: 1, name: 'KTP / Passport', description: 'Valid identity document', required: true, status: 'Received', expiry: null, version: 1 },
  { id: 2, name: 'NPWP', description: 'Tax registration number', required: true, status: 'Received', expiry: null, version: 1 },
  { id: 3, name: 'Akta Pendirian + Perubahan', description: 'Deed of establishment (Corporate)', required: false, status: 'Received', expiry: null, version: 2 },
  { id: 4, name: 'Laporan Keuangan 3 Tahun', description: 'Audited / management accounts', required: true, status: 'Pending', expiry: null, version: null },
  { id: 5, name: 'Rekening Koran 6 Bulan', description: 'Bank statements last 6 months', required: true, status: 'Pending', expiry: null, version: null },
  { id: 6, name: 'SIUP / NIB', description: 'Business license', required: false, status: 'Received', expiry: '2027-03', version: 1 },
  { id: 7, name: 'Sertifikat Jaminan (SHM)', description: 'Collateral ownership cert', required: false, status: 'Missing', expiry: null, version: null },
  { id: 8, name: 'Asuransi Jiwa / BPJS', description: 'Life insurance policy', required: false, status: 'Pending', expiry: null, version: null },
])

const uploadedFiles = ref([
  { name: 'KTP_Budi_Santoso.pdf', size: '1.2 MB', uploaded: 'Today 09:15' },
  { name: 'NPWP_scan.jpg', size: '856 KB', uploaded: 'Today 09:16' },
])

const ratios = [
  { label: 'DSCR', value: '1.42x', ok: true },
  { label: 'DER', value: '1.8x', ok: true },
  { label: 'Current Ratio', value: '1.65x', ok: true },
  { label: 'EBITDA Margin', value: '18.4%', ok: true },
  { label: 'ROA', value: '6.2%', ok: true },
  { label: 'ROE', value: '14.8%', ok: true },
  { label: 'Working Capital', value: '32 days', ok: true },
  { label: 'NPL Indicator', value: '0%', ok: true },
]

const spreadingRows = [
  { label: 'Revenue', values: ['Rp 28.4B', 'Rp 33.1B', 'Rp 38.7B'], bold: false },
  { label: 'Cost of Goods Sold', values: ['Rp 20.1B', 'Rp 23.4B', 'Rp 27.2B'], bold: false, indent: true },
  { label: 'Gross Profit', values: ['Rp 8.3B', 'Rp 9.7B', 'Rp 11.5B'], bold: true },
  { label: 'EBITDA', values: ['Rp 5.1B', 'Rp 6.0B', 'Rp 7.1B'], bold: true },
  { label: 'Net Profit', values: ['Rp 3.2B', 'Rp 3.9B', 'Rp 4.6B'], bold: true },
  { label: 'Total Assets', values: ['Rp 42.0B', 'Rp 48.5B', 'Rp 56.3B'], bold: false },
  { label: 'Total Debt', values: ['Rp 18.5B', 'Rp 20.1B', 'Rp 22.8B'], bold: false },
  { label: 'Net Worth', values: ['Rp 23.5B', 'Rp 28.4B', 'Rp 33.5B'], bold: true },
]

const fiveC = [
  { label: 'Character (KYC & History)', score: 80 },
  { label: 'Capacity (DSR / Cashflow)', score: 72 },
  { label: 'Capital (Net Worth)', score: 68 },
  { label: 'Collateral (LTV)', score: 85 },
  { label: 'Conditions (Industry Risk)', score: 64 },
]

const collaterals = [
  { id: 'COL-001', name: 'Gudang Industri Bekasi', icon: 'home', value: 8500000000, ltv: 65, status: 'Appraised', insured: 'Dec 2027' },
  { id: 'COL-002', name: 'Mesin CNC Haas VF-4', icon: 'tool', value: 3200000000, ltv: 70, status: 'Appraised', insured: 'Jun 2027' },
  { id: 'COL-003', name: 'Deposito BCA', icon: 'credit-card', value: 1500000000, ltv: 90, status: 'Pledged', insured: 'N/A' },
]

const appraisals = [
  { col: 'Gudang Bekasi', appraiser: 'PT KJPP Sapta Sentosa', value: 8500000000, date: '2026-03-10', next: '2027-03-10', status: 'Completed' },
  { col: 'Mesin CNC', appraiser: 'PT Surveyor Indonesia', value: 3200000000, date: '2026-04-02', next: '2027-04-02', status: 'Completed' },
  { col: 'Deposito BCA', appraiser: 'Internal', value: 1500000000, date: '2026-05-01', next: 'On maturity', status: 'Completed' },
]

const approvalLevels = ref([
  { id: 1, approver: 'Dewi Kusuma', role: 'Relationship Manager', state: 'Approved', date: '22 May 2026', note: 'Borrower profile strong, recommend approval.' },
  { id: 2, approver: 'Ahmad Fauzi', role: 'Credit Head', state: 'Approved', date: '23 May 2026', note: 'Financial ratios satisfactory. Proceed to committee.' },
  { id: 3, approver: 'Sari Indrawati', role: 'Risk Officer', state: 'Pending', date: null, note: null },
  { id: 4, approver: 'Bimo Prakoso', role: 'Division Director', state: 'Waiting', date: null, note: null },
])

const committeeMembers = ref([
  { name: 'Ahmad Fauzi', role: 'Credit Head', vote: 'Approve' },
  { name: 'Sari Indrawati', role: 'Risk Officer', vote: 'Approve' },
  { name: 'Bimo Prakoso', role: 'Division Director', vote: 'Approve' },
  { name: 'Rina Putri', role: 'Compliance', vote: null },
])

const agreements = [
  { id: 1, name: 'Perjanjian Kredit (PK)', version: 'v2.1', date: '24 May 2026', status: 'Pending Signature' },
  { id: 2, name: 'Perjanjian Pengikatan Jaminan (PPJ)', version: 'v1.0', date: '24 May 2026', status: 'Draft' },
  { id: 3, name: 'Akta Notaris — Fidusia', version: 'v1.0', date: 'Pending', status: 'Draft' },
]

const signers = ref([
  { name: 'Dewi Kusuma', role: 'Bank Officer', signed: true, signed_at: '24 May 09:14' },
  { name: 'PT Maju Bersama', role: 'Borrower', signed: true, signed_at: '24 May 11:32' },
  { name: 'Bimo Prakoso', role: 'Director', signed: false, signed_at: null },
])

const covenants = [
  { id: 1, name: 'DSCR ≥ 1.2x', type: 'Financial', threshold: '≥ 1.2x', frequency: 'Semi-annual' },
  { id: 2, name: 'DER ≤ 2.5x', type: 'Financial', threshold: '≤ 2.5x', frequency: 'Annual' },
  { id: 3, name: 'No additional indebtedness > Rp 5B', type: 'Non-Financial', threshold: 'Rp 5B cap', frequency: 'Ongoing' },
  { id: 4, name: 'Insurance maintained at all times', type: 'Non-Financial', threshold: 'Active policy', frequency: 'Annual' },
]

const cpItems = ref([
  { id: 1, name: 'Signed loan agreement (PK) received', cleared: true },
  { id: 2, name: 'Collateral registered & insured', cleared: true },
  { id: 3, name: 'NPWP validation confirmed', cleared: true },
  { id: 4, name: 'Notarial deed executed', cleared: false },
  { id: 5, name: 'Insurance beneficiary changed to bank', cleared: false },
])

const tranches = [
  { id: 1, amount: 7500000000, date: '28 May 2026', condition: 'Initial disbursement upon CP clearance', status: 'Pending' },
  { id: 2, amount: 3000000000, date: '28 Aug 2026', condition: 'Upon progress report — 60% utilization confirmed', status: 'Planned' },
  { id: 3, amount: 2000000000, date: '28 Nov 2026', condition: 'Final tranche — project completion certificate', status: 'Planned' },
]

const healthKpis = [
  { label: 'Outstanding Balance', value: 'Rp 11.2B', color: 'text-slate-800', barColor: 'bg-teal-500', pct: 89 },
  { label: 'Paid to Date', value: 'Rp 1.3B', color: 'text-teal-600', barColor: 'bg-green-500', pct: 11 },
  { label: 'Days Past Due', value: '0 days', color: 'text-green-600', barColor: 'bg-green-500', pct: 0 },
  { label: 'Installment Cover', value: '1.42x', color: 'text-teal-600', barColor: 'bg-teal-500', pct: 71 },
]

const paymentRows = [
  { n: 1, due: '28 Jun 2026', scheduled: 58900000, paid: 58900000, outstanding: 11141100000, status: 'Paid' },
  { n: 2, due: '28 Jul 2026', scheduled: 58900000, paid: 58900000, outstanding: 11082200000, status: 'Paid' },
  { n: 3, due: '28 Aug 2026', scheduled: 58900000, paid: null, outstanding: 11082200000, status: 'Due' },
  { n: 4, due: '28 Sep 2026', scheduled: 58900000, paid: null, outstanding: null, status: 'Upcoming' },
  { n: 5, due: '28 Oct 2026', scheduled: 58900000, paid: null, outstanding: null, status: 'Upcoming' },
  { n: 6, due: '28 Nov 2026', scheduled: 58900000, paid: null, outstanding: null, status: 'Upcoming' },
]

const covenantMonitoring = [
  { id: 1, name: 'DSCR', threshold: '≥ 1.2x', actual: '1.42x', ok: true, pct: 71 },
  { id: 2, name: 'Debt-to-Equity Ratio', threshold: '≤ 2.5x', actual: '1.8x', ok: true, pct: 72 },
  { id: 3, name: 'Current Ratio', threshold: '≥ 1.2x', actual: '1.65x', ok: true, pct: 83 },
]

// ── Computed ──
const filteredApps = computed(() => {
  const q = searchQuery.value.toLowerCase()
  return q ? apps.value.filter(a => (a.borrower_name + a.id).toLowerCase().includes(q)) : apps.value
})

const docsReceived = computed(() => documents.value.filter(d => d.status === 'Received').length)
const docsPending = computed(() => documents.value.filter(d => d.status === 'Pending').length)
const docsMissing = computed(() => documents.value.filter(d => d.status === 'Missing' && d.required).length)

// ── Methods ──
function __(s) { return s }
function initials(name) { return (name||'?').split(' ').slice(0,2).map(w=>w[0]).join('').toUpperCase() }
function fmt(v) { return v ? 'Rp ' + Math.round(v).toLocaleString('id-ID') : '—' }

function statusBadge(s) {
  const m = { Draft:'bg-slate-100 text-slate-600', 'Document Collection':'bg-amber-100 text-amber-700', 'Credit Analysis':'bg-blue-100 text-blue-700', Committee:'bg-purple-100 text-purple-700', Active:'bg-green-100 text-green-700', Rejected:'bg-red-100 text-red-600' }
  return m[s] || 'bg-slate-100 text-slate-600'
}

function selectApp(app) {
  selected.value = app
  currentStep.value = app.step || 1
  form.value.borrower_name = app.borrower_name || ''
  form.value.borrower_type = app.borrower_type || 'Individual'
  form.value.facility_type = app.facility_type || ''
  form.value.requested_amount = app.requested_amount || 0
}

function jumpStep(id) {
  if (id <= (selected.value?.step || 1) + 1) currentStep.value = id
}

async function nextStep() {
  if (currentStep.value >= 8) return
  if (currentStep.value <= 3) {
    saving.value = true
    await mockSave()
    saving.value = false
    triggerAutoSaved()
  }
  currentStep.value++
  if (selected.value) selected.value.step = Math.max(selected.value.step || 1, currentStep.value)
}

function prevStep() { if (currentStep.value > 1) currentStep.value-- }

function mockSave() {
  return new Promise(resolve => setTimeout(resolve, 600))
}

function triggerAutoSaved() {
  autoSaved.value = true
  setTimeout(() => { autoSaved.value = false }, 3000)
}

function startNew() {
  newApp.value = { borrower_name: '', borrower_type: 'Individual' }
  showModal.value = true
}

function createApp() {
  if (!newApp.value.borrower_name) return
  const id = 'LOS-2026-00' + (apps.value.length + 5)
  const app = { id, borrower_name: newApp.value.borrower_name, borrower_type: newApp.value.borrower_type, step: 1, status: 'Draft', facility_type: '', requested_amount: 0 }
  apps.value.unshift(app)
  showModal.value = false
  selectApp(app)
}

function cycleKyc(kyc) {
  const cycle = ['Not Submitted', 'Pending', 'Verified']
  kyc.status = cycle[(cycle.indexOf(kyc.status) + 1) % cycle.length]
}

function cycleDoc(doc) {
  const cycle = ['Pending', 'Received', 'Missing', 'Waived']
  doc.status = cycle[(cycle.indexOf(doc.status) + 1) % cycle.length]
}

function fakeNpwpValidate() {
  if (!form.value.npwp) return
  npwpStatus.value = '...'
  setTimeout(() => { npwpStatus.value = '✓ Valid' }, 900)
}

function fakeOcr(kyc) {
  ocrResult.value = null
  setTimeout(() => {
    ocrResult.value = [
      { key: 'NIK', value: '3171xxxxxxxxxxxx', conf: 98 },
      { key: 'Nama', value: form.value.borrower_name || 'Budi Santoso', conf: 96 },
      { key: 'TTL', value: 'Jakarta, 15 Mar 1985', conf: 91 },
      { key: 'Alamat', value: 'Jl. Sudirman No. 12, Jakarta Selatan', conf: 88 },
      { key: 'Kelamin', value: 'Laki-laki', conf: 99 },
      { key: 'Berlaku', value: 'Seumur Hidup', conf: 95 },
    ]
    kyc.status = 'Verified'
  }, 800)
}

function applyOcr() {
  if (!ocrResult.value) return
  const nama = ocrResult.value.find(r => r.key === 'Nama')
  if (nama && !form.value.borrower_name) form.value.borrower_name = nama.value
  ocrResult.value = null
  triggerAutoSaved()
}

function fakeUpload() {
  const names = ['Laporan_Keuangan_2024.pdf','Rekening_Koran_BCA.pdf','SIUP_2026.pdf']
  uploadingFile.value = names[Math.floor(Math.random()*names.length)]
  uploadProgress.value = 0
  const iv = setInterval(() => {
    uploadProgress.value += 20
    if (uploadProgress.value >= 100) {
      clearInterval(iv)
      uploadedFiles.value.push({ name: uploadingFile.value, size: (Math.random()*4+0.5).toFixed(1)+' MB', uploaded: 'Just now' })
      setTimeout(() => { uploadProgress.value = 0; uploadingFile.value = '' }, 800)
    }
  }, 200)
}

function confirmDelete(app) {
  deleteTarget.value = app
}

function deleteApp() {
  if (!deleteTarget.value) return
  apps.value = apps.value.filter(a => a.id !== deleteTarget.value.id)
  if (selected.value?.id === deleteTarget.value.id) {
    selected.value = null
    currentStep.value = 1
  }
  deleteTarget.value = null
}

// Auto-save every 30s when step <= 3
let autoSaveTimer = null
onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
  autoSaveTimer = setInterval(() => {
    if (selected.value && currentStep.value <= 3) triggerAutoSaved()
  }, 30000)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
  if (autoSaveTimer) clearInterval(autoSaveTimer)
})
</script>

<style scoped>
.field-label { @apply block text-xs font-semibold text-gray-700 mb-1.5; }
.field-input { @apply w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-teal-500 transition-colors; }
.field-select { @apply w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-teal-500 bg-white transition-colors; }
</style>
