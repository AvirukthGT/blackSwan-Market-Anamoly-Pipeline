{% macro generate_schema_name(custom_schema_name, node) -%}

    {%- set default_schema = target.schema -%}

    {%- if custom_schema_name is none -%}
        {# If no schema is specified, use the default from profiles.yml #}
        {{ default_schema }}

    {%- else -%}
        {# If a schema is specified (like 'mart'), use it EXACTLY #}
        {{ custom_schema_name | trim }}

    {%- endif -%}

{%- endmacro %}
