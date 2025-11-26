<%!
import re
%>
<%def name="render_string(string)">
<%
    lines = string.splitlines()
    indented = '\n'.join('    ' + line if line else '' for line in lines)
%>${indented}
</%def>
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | default("None")}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
${render_string(upgrade_ops)}


def downgrade() -> None:
${render_string(downgrade_ops)}
