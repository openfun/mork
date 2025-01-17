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
- name: MORK_API_SERVER_HOST
  value: "{{ include "mork.fullname" . }}-api"
- name: MORK_API_SERVER_PORT
  value: "{{ .Values.api.port }}"
- name: MORK_API_KEYS
  valueFrom:
    secretKeyRef:
      name: mork-api-keys
      key: MORK_API_KEYS
- name: MORK_DELETION_PERIOD
  value: "{{ .Values.deletion.period }}"
- name: MORK_DELETE_MAX_RETRIES
  value: "{{ .Values.deletion.maxRetries }}"
- name: MORK_EDX_FORUM_PLACEHOLDER_USER_ID
  value: "{{ .Values.deletion.forumUserId }}"
- name: MORK_DB_ENGINE
  value: "{{ .Values.db.engine }}"
- name: MORK_DB_HOST
  value: "{{ .Values.db.host }}"
- name: MORK_DB_NAME
  value: "{{ .Values.db.name }}"
- name: MORK_DB_USER
  value: "{{ .Values.db.user }}"
- name: MORK_DB_PASSWORD
  valueFrom:
    secretKeyRef:
      name: mork-database
      key: MORK_DB_PASSWORD
- name: MORK_DB_PORT
  value: "{{ .Values.db.port }}"
- name: MORK_DB_DEBUG
  value: "{{ .Values.db.debug }}"
- name: MORK_EDX_MYSQL_DB_ENGINE
  value: "{{ .Values.edx.mysql.engine }}"
- name: MORK_EDX_MYSQL_DB_HOST
  value: "{{ .Values.edx.mysql.host }}"
- name: MORK_EDX_MYSQL_DB_NAME
  value: "{{ .Values.edx.mysql.name }}"
- name: MORK_EDX_MYSQL_DB_USER
  value: "{{ .Values.edx.mysql.user }}"
- name: MORK_EDX_MYSQL_DB_PASSWORD
  valueFrom:
    secretKeyRef:
      name: mork-edx-database
      key: MORK_EDX_MYSQL_DB_PASSWORD
- name: MORK_EDX_MYSQL_DB_PORT
  value: "{{ .Values.edx.mysql.port }}"
- name: MORK_EDX_MYSQL_DB_DEBUG
  value: "{{ .Values.edx.mysql.debug }}"
- name: MORK_EDX_MONGO_DB_ENGINE
  value: "{{ .Values.edx.mongo.engine }}"
- name: MORK_EDX_MONGO_DB_HOST
  value: "{{ .Values.edx.mongo.host }}"
- name: MORK_EDX_MONGO_DB_NAME
  value: "{{ .Values.edx.mongo.name }}"
- name: MORK_EDX_MONGO_DB_USER
  value: "{{ .Values.edx.mongo.user }}"
- name: MORK_EDX_MONGO_DB_PASSWORD
  valueFrom:
    secretKeyRef:
      name: mork-edx-database
      key: MORK_EDX_MONGO_DB_PASSWORD
- name: MORK_EDX_MONGO_DB_PORT
  value: "{{ .Values.edx.mongo.port }}"
- name: MORK_EDX_MONGO_DB_DEBUG
  value: "{{ .Values.edx.mongo.debug }}"
- name: MORK_BREVO_API_URL
  value: "{{ .Values.brevo.apiUrl }}"
- name: MORK_BREVO_API_KEY
  valueFrom:
    secretKeyRef:
      name: mork-brevo-api-key
      key: MORK_BREVO_API_KEY
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
- name: "MORK_WARNING_PERIOD"
  value: "{{ .Values.email.period }}"
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
- name: MORK_SENTRY_DSN
  value: "{{ .Values.sentry.dsn }}"
- name: MORK_SENTRY_EXECUTION_ENVIRONMENT
  value: "{{ .Values.sentry.environment }}"
- name: MORK_SENTRY_API_TRACES_SAMPLE_RATE
  value: "{{ .Values.sentry.apiSampleRate }}"
- name: MORK_SENTRY_CELERY_TRACES_SAMPLE_RATE
  value: "{{ .Values.sentry.celerySampleRate }}"
- name: MORK_SENTRY_IGNORE_HEALTH_CHECKS
  value: "{{ .Values.sentry.ignoreHealthChecks }}"

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
