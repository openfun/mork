{{/*
Expand the name of the chart.
*/}}
{{- define "mork.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "mork.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "mork.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "mork.labels" -}}
helm.sh/chart: {{ include "mork.chart" . }}
{{ include "mork.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "mork.selectorLabels" -}}
app.kubernetes.io/name: {{ include "mork.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/part-of: mork
{{- end }}

{{/*
Environment variables
*/}}
{{- define "mork.envs" -}}
- name: "MORK_API_SERVER_PORT"
  value: "{{ .Values.api.port }}"
- name: "MORK_API_KEYS"
  valueFrom:
    secretKeyRef:
      name: mork-api-keys
      key: MORK_API_KEYS
- name: "MORK_DB_ENGINE"
  value: "{{ .Values.db.engine }}"
- name: "MORK_DB_HOST"
  value: "{{ .Values.db.host }}"
- name: "MORK_DB_NAME"
  value: "{{ .Values.db.name }}"
- name: "MORK_DB_USER"
  value: "{{ .Values.db.user }}"
- name: "MORK_DB_PASSWORD"
  valueFrom:
    secretKeyRef:
      name: mork-database
      key: MORK_DB_PASSWORD
- name: MORK_DB_PORT
  value: "{{ .Values.db.port }}"
- name: MORK_DB_DEBUG
  value: "{{ .Values.db.debug }}"
- name: MORK_EDX_DB_ENGINE
  value: "{{ .Values.edx.db.engine }}"
- name: MORK_EDX_DB_HOST
  value: "{{ .Values.edx.db.host }}"
- name: MORK_EDX_DB_NAME
  value: "{{ .Values.edx.db.name }}"
- name: MORK_EDX_DB_USER
  value: "{{ .Values.edx.db.user }}"
- name: MORK_EDX_DB_PASSWORD
  valueFrom:
    secretKeyRef:
      name: mork-edx-database
      key: MORK_EDX_DB_PASSWORD
- name: MORK_EDX_DB_PORT
  value: "{{ .Values.edx.db.port }}"
- name: MORK_EDX_DB_DEBUG
  value: "{{ .Values.edx.db.debug }}"
- name: MORK_CELERY_BROKER_URL
  value: "{{ .Values.celery.brokerUrl }}"
- name: MORK_CELERY_BROKER_TRANSPORT_OPTIONS
  value: {{ .Values.celery.brokerTransportOptions | squote }}
- name: MORK_CELERY_RESULT_BACKEND
  value: "{{ .Values.celery.resultBackend }}"
- name: MORK_CELERY_RESULT_BACKEND_TRANSPORT_OPTIONS
  value: {{ .Values.celery.resultBackendTransportOptions | squote }}
- name: MORK_CELERY_TASK_DEFAULT_QUEUE
  value: "{{ .Values.celery.taskDefaultQueue }}"
- name: MORK_EMAIL_HOST
  value: "{{ .Values.email.host }}"
- name: MORK_EMAIL_HOST_USER
  value: "{{ .Values.email.user }}"
- name: MORK_EMAIL_HOST_PASSWORD
  valueFrom:
    secretKeyRef:
      name: mork-email
      key: MORK_EMAIL_HOST_PASSWORD
- name: MORK_EMAIL_PORT
  value: "{{ .Values.email.port }}"
- name: MORK_EMAIL_USE_TLS
  value: "{{ .Values.email.useTls }}"
- name: MORK_EMAIL_FROM
  value: "{{ .Values.email.from }}"
- name: MORK_EMAIL_RATE_LIMIT
  value: "{{ .Values.email.rateLimit }}"
- name: MORK_EMAIL_MAX_RETRIES
  value: "{{ .Values.email.maxRetries }}"
- name: MORK_EMAIL_SITE_NAME
  value: "{{ .Values.email.siteName }}"
- name: MORK_EMAIL_SITE_BASE_URL
  value: "{{ .Values.email.siteBaseUrl }}"
- name: MORK_EMAIL_SITE_LOGIN_URL
  value: "{{ .Values.email.siteLoginUrl }}"

{{- range $key, $val := .Values.env.secret }}
- name: {{ $val.envName }}
  valueFrom:
    secretKeyRef:
      name: {{ $val.secretName }}
      key: {{ $val.keyName }}
{{- end }}
{{- end }}

{{/*
ImagePullSecrets
*/}}
{{- define "mork.imagePullSecrets" -}}
{{- $pullSecrets := .Values.imagePullSecrets }}
{{- if (not (empty $pullSecrets)) }}
imagePullSecrets:
{{- range $pullSecrets }}
- name: {{ . }}
{{ end }}
{{- end -}}
{{- end }}
