{{/*
Expand the name of the chart.
*/}}
{{- define "data-visualizer.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "data-visualizer.fullname" -}}
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
{{- define "data-visualizer.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "data-visualizer.labels" -}}
helm.sh/chart: {{ include "data-visualizer.chart" . }}
{{ include "data-visualizer.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "data-visualizer.selectorLabels" -}}
app.kubernetes.io/name: {{ include "data-visualizer.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Flask labels
*/}}
{{- define "data-visualizer.flask.labels" -}}
{{- include "data-visualizer.labels" . }}
app.kubernetes.io/component: flask
{{- end }}

{{/*
React labels
*/}}
{{- define "data-visualizer.react.labels" -}}
{{- include "data-visualizer.labels" . }}
app.kubernetes.io/component: react
{{- end }}

{{/*
Flask selector labels
*/}}
{{- define "data-visualizer.flask.selectorLabels" -}}
{{- include "data-visualizer.selectorLabels" . }}
app.kubernetes.io/component: flask
{{- end }}

{{/*
React selector labels
*/}}
{{- define "data-visualizer.react.selectorLabels" -}}
{{- include "data-visualizer.selectorLabels" . }}
app.kubernetes.io/component: react
{{- end }}


{{/*
Create the name of the service account to use
*/}}
{{- define "data-visualizer.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "data-visualizer.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}