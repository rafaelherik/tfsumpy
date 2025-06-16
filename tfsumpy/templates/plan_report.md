# Terraform Plan Analysis Report

Generated on: {{ timestamp }}

## Summary
- **Total Resources**: {{ summary.total_resources }}
- **Resources to Add**: {{ summary.resources_to_add }}
- **Resources to Change**: {{ summary.resources_to_change }}
- **Resources to Destroy**: {{ summary.resources_to_destroy }}

## Resource Changes
{% for resource in resources %}
{% if "delete" in resource.actions and "create" in resource.actions %}
```hcl
-/+ {{ resource.resource_type }} - **{{ resource.identifier }}** {
{% if resource.module %}
    module  = "{{ resource.module }}"
{% endif %}
{% if resource.changes %}
{% for change in resource.changes %}
{% if change.before is none and change.after is not none %}
    + {{ change.attribute }} = {{ change.after|to_json }}
{% elif change.before is not none and change.after is none %}
    - {{ change.attribute }} = {{ change.before|to_json }}
{% else %}
    ~ {{ change.attribute }} = {{ change.before|to_json }} -> {{ change.after|to_json }}
{% endif %}
{% endfor %}
{% endif %}
}
```
{% elif "create" in resource.actions %}
```hcl
+ {{ resource.resource_type }} - **{{ resource.identifier }}** {
{% if resource.module %}
    module  = "{{ resource.module }}"
{% endif %}
{% if resource.changes %}
{% for change in resource.changes %}
{% if change.before is none and change.after is not none %}
    + {{ change.attribute }} = {{ change.after|to_json }}
{% elif change.before is not none and change.after is none %}
    - {{ change.attribute }} = {{ change.before|to_json }}
{% else %}
    ~ {{ change.attribute }} = {{ change.before|to_json }} -> {{ change.after|to_json }}
{% endif %}
{% endfor %}
{% endif %}
}
```
{% elif "update" in resource.actions %}
```hcl
~ {{ resource.resource_type }} - **{{ resource.identifier }}** {
{% if resource.module %}
    module  = "{{ resource.module }}"
{% endif %}
{% if resource.changes %}
{% for change in resource.changes %}
{% if change.before is none and change.after is not none %}
    + {{ change.attribute }} = {{ change.after|to_json }}
{% elif change.before is not none and change.after is none %}
    - {{ change.attribute }} = {{ change.before|to_json }}
{% else %}
    ~ {{ change.attribute }} = {{ change.before|to_json }} -> {{ change.after|to_json }}
{% endif %}
{% endfor %}
{% endif %}
}
```
{% elif "delete" in resource.actions %}
```hcl
- {{ resource.resource_type }} - **{{ resource.identifier }}** {
{% if resource.module %}
    module  = "{{ resource.module }}"
{% endif %}
{% if resource.changes %}
{% for change in resource.changes %}
{% if change.before is none and change.after is not none %}
    + {{ change.attribute }} = {{ change.after|to_json }}
{% elif change.before is not none and change.after is none %}
    - {{ change.attribute }} = {{ change.before|to_json }}
{% else %}
    ~ {{ change.attribute }} = {{ change.before|to_json }} -> {{ change.after|to_json }}
{% endif %}
{% endfor %}
{% endif %}
}
```
{% endif %}
{% endfor %}

{% if ai_summary %}
## AI Analysis

{{ ai_summary }}
{% endif %}

