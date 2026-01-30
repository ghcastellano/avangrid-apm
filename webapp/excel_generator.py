"""
Excel Generator for Avangrid APM Platform
Generates a full Excel workbook matching the original APM format with:
Calculator, Dashboard, Strategic Roadmap, Application Groups, Value Chain,
and individual application sheets.
"""

import io
import re
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import ScatterChart, Reference, Series
from openpyxl.chart.label import DataLabelList
from openpyxl.chart.marker import Marker
from openpyxl.chart.series import DataPoint
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from database import (
    get_session, close_session,
    Application, QuestionnaireAnswer, TranscriptAnswer, DavidNote, SynergyScore
)

# ============================================================
# Constants
# ============================================================

SYNERGY_BLOCKS = {
    'Strategic Fit': {'Type': 'Business', 'Weight': 30},
    'Business Efficiency': {'Type': 'Business', 'Weight': 30},
    'User Value': {'Type': 'Business', 'Weight': 20},
    'Financial Value': {'Type': 'Business', 'Weight': 20},
    'Architecture': {'Type': 'Technical', 'Weight': 30},
    'Operational Risk': {'Type': 'Technical', 'Weight': 30},
    'Maintainability': {'Type': 'Technical', 'Weight': 25},
    'Support Quality': {'Type': 'Technical', 'Weight': 15},
}

BLOCK_DEFINITIONS = {
    'Strategic Fit': {1: 'Completely misaligned', 2: 'Partially aligned', 3: 'Neutral', 4: 'Well-aligned', 5: 'Strategic driver'},
    'Business Efficiency': {1: 'Manual', 2: 'Low efficiency', 3: 'Average', 4: 'High', 5: 'Optimized'},
    'User Value': {1: 'Rejected', 2: 'Low satisfaction', 3: 'Acceptable', 4: 'Good', 5: 'Delightful'},
    'Financial Value': {1: 'Negative', 2: 'Poor', 3: 'Neutral', 4: 'Positive', 5: 'Exceptional'},
    'Architecture': {1: 'Obsolete', 2: 'Aging', 3: 'Stable', 4: 'Modern', 5: 'Future-proof'},
    'Operational Risk': {1: 'Critical', 2: 'High', 3: 'Managed', 4: 'Low', 5: 'Fortified'},
    'Maintainability': {1: 'Impossible', 2: 'Hard', 3: 'Standard', 4: 'Good', 5: 'Excellent'},
    'Support Quality': {1: 'Non-existent', 2: 'Reactive', 3: 'Defined', 4: 'Proactive', 5: 'World-class'},
}

REC_COLORS = {
    'EVOLVE': {'fill': 'C6EFCE', 'font': '006100'},
    'INVEST': {'fill': 'FFEB9C', 'font': '9C5700'},
    'MAINTAIN': {'fill': 'BDD7EE', 'font': '0066CC'},
    'ELIMINATE': {'fill': 'FFC7CE', 'font': '9C0006'},
}

MATRIX_CONFIG = [
    ('ELIMINATE', 'Replace', 'P1 - Critical', 'High Risk / EOL.'),
    ('ELIMINATE', 'Retire', 'P1 - Critical', 'Decommission'),
    ('ELIMINATE', 'Absorbed', 'P2 - Tactical', 'Consolidation'),
    ('INVEST', 'Absorb', 'P1 - Critical', 'High Value Opportunity'),
    ('INVEST', 'Modernize', 'P1 - Critical', 'Transformation'),
    ('EVOLVE', 'Migrate', 'P1 - Critical', 'Platform shift'),
    ('EVOLVE', 'Enhance', 'P2 - Strategic', 'Expansion'),
    ('EVOLVE', 'Refactor', 'P2 - Strategic', 'Code quality'),
    ('EVOLVE', 'Upgrade', 'P2 - Strategic', 'Version'),
    ('MAINTAIN', 'Internalize', 'P2 - Compliance', 'Governance'),
    ('MAINTAIN', 'Maintain', 'P3 - Routine', 'Keep lights on'),
]

APP_GROUP_CATEGORIES = {
    'Task Management / User Alignment': {
        'color': 'E87722',
        'keywords': ['task', 'schedule', 'track', 'assign', 'user', 'alignment', 'collab', 'arcos', 'jums', 'switching', 'ppe']
    },
    'Maintenance & Asset Mgmt': {
        'color': '0066B3',
        'keywords': ['maintain', 'asset', 'work order', 'inspection', 'repair', 'lifecycle', 'bentley', 'cimplicity', 'cathodic', 'poleforeman', 'esosr']
    },
    'Grid Operations / Engineering': {
        'color': '00B050',
        'keywords': ['scada', 'dms', 'oms', 'real-time', 'grid', 'voltage', 'design', 'model', 'calculate', 'engineer', 'kaffa', 'scal', 'dsd']
    },
    'Document / Info Management': {
        'color': '7030A0',
        'keywords': ['document', 'file', 'map', 'drawing', 'view', 'repository', 'knowledge', 'projectwise', 'mapping']
    },
    'Corporate / Administrative': {
        'color': 'FFC000',
        'keywords': ['finance', 'hr', 'legal', 'compliance', 'security', 'supply chain', 'admin', 'erp', 'sap']
    },
}

VALUE_CHAIN_STAGES = {
    'Generation (Renewables)': {
        'color': '00B0F0',
        'keywords': ['generation', 'renewable', 'wind', 'solar', 'hydro', 'offshore', 'onshore', 'plant', 'turbine', 'energy source', 'production']
    },
    'Transmission (Transport)': {
        'color': '0070C0',
        'keywords': ['transmission', 'high voltage', 'substation', 'interconnection', 'control center', 'ecc', 'tcc', 'line', 'relay', 'protection']
    },
    'Distribution (Delivery)': {
        'color': '00B050',
        'keywords': ['distribution', 'medium voltage', 'low voltage', 'ami', 'smart grid', 'meter', 'outage', 'oms', 'dms', 'scada', 'field', 'pole', 'circuit']
    },
    'Customer Solutions': {
        'color': 'FFC000',
        'keywords': ['customer', 'billing', 'crm', 'call center', 'service', 'payment', 'meter to cash', 'der', 'ev charging', 'portal', 'account']
    },
    'Corporate / Shared Services': {
        'color': '7030A0',
        'keywords': ['finance', 'hr', 'legal', 'compliance', 'security', 'supply chain', 'admin', 'it', 'procurement', 'cybersecurity', 'ehs']
    },
}

# Common styles
THIN_BORDER = Border(
    left=Side(style='thin'), right=Side(style='thin'),
    top=Side(style='thin'), bottom=Side(style='thin')
)
HEADER_FONT = Font(name='Calibri', size=11, bold=True, color='FFFFFF')
HEADER_FILL_DARK = PatternFill(start_color='333333', end_color='333333', fill_type='solid')
HEADER_FILL_ORANGE = PatternFill(start_color='E87722', end_color='E87722', fill_type='solid')
HEADER_FILL_BLUE = PatternFill(start_color='0066B3', end_color='0066B3', fill_type='solid')
CONTENT_FONT = Font(name='Calibri', size=10)
CONTENT_FILL = PatternFill(start_color='FAFAFA', end_color='FAFAFA', fill_type='solid')
WRAP_ALIGN = Alignment(wrap_text=True, vertical='top')


def sanitize_sheet_name(name):
    """Make a valid Excel sheet name (max 31 chars, no special chars)."""
    clean = re.sub(r'[\[\]:*?/\\\'"]', '', name)
    return clean[:31]


def get_recommendation(bvi, thi):
    if bvi >= 60 and thi >= 60:
        return 'EVOLVE'
    elif bvi >= 60 and thi < 60:
        return 'INVEST'
    elif bvi < 60 and thi >= 60:
        return 'MAINTAIN'
    else:
        return 'ELIMINATE'


def calculate_bvi_thi(scores, custom_weights=None):
    """Calculate BVI and THI from block scores."""
    weights = custom_weights or SYNERGY_BLOCKS
    bvi_blocks = ['Strategic Fit', 'Business Efficiency', 'User Value', 'Financial Value']
    thi_blocks = ['Architecture', 'Operational Risk', 'Maintainability', 'Support Quality']

    bvi_total = sum(scores.get(b, 0) * weights.get(b, {}).get('Weight', SYNERGY_BLOCKS[b]['Weight']) for b in bvi_blocks)
    bvi_weight = sum(weights.get(b, {}).get('Weight', SYNERGY_BLOCKS[b]['Weight']) for b in bvi_blocks)
    bvi = (bvi_total / bvi_weight * 20) if bvi_weight > 0 else 0

    thi_total = sum(scores.get(b, 0) * weights.get(b, {}).get('Weight', SYNERGY_BLOCKS[b]['Weight']) for b in thi_blocks)
    thi_weight = sum(weights.get(b, {}).get('Weight', SYNERGY_BLOCKS[b]['Weight']) for b in thi_blocks)
    thi = (thi_total / thi_weight * 20) if thi_weight > 0 else 0

    return round(bvi, 1), round(thi, 1)


def categorize_app(app_name, qa_texts):
    """Categorize an application into groups based on name and Q&A content."""
    search_text = (app_name + " " + " ".join(qa_texts)).lower()
    for cat_name, cat_info in APP_GROUP_CATEGORIES.items():
        for kw in cat_info['keywords']:
            if kw in search_text:
                return cat_name
    return 'Uncategorized'


def categorize_value_chain(app_name, qa_texts):
    """Categorize an application into value chain stage."""
    search_text = (app_name + " " + " ".join(qa_texts)).lower()
    for stage_name, stage_info in VALUE_CHAIN_STAGES.items():
        for kw in stage_info['keywords']:
            if kw in search_text:
                return stage_name
    return 'Cross-Cutting'


# ============================================================
# Sheet builders
# ============================================================

def build_calculator_sheet(wb, apps_data, custom_weights):
    """Build the Calculator sheet with scores, BVI, THI, and recommendations."""
    ws = wb.create_sheet("Calculator", 0)
    blocks = list(SYNERGY_BLOCKS.keys())

    # Column widths
    ws.column_dimensions['A'].width = 30
    for i in range(len(blocks)):
        ws.column_dimensions[get_column_letter(i + 2)].width = 18
    ws.column_dimensions[get_column_letter(len(blocks) + 2)].width = 22
    ws.column_dimensions[get_column_letter(len(blocks) + 3)].width = 22
    ws.column_dimensions[get_column_letter(len(blocks) + 4)].width = 18

    # Row 1: Headers
    ws.cell(row=1, column=1, value="Application Name").font = Font(name='Calibri', size=11, bold=True)
    ws['A1'].fill = HEADER_FILL_DARK
    ws['A1'].font = HEADER_FONT
    ws['A1'].border = THIN_BORDER

    for i, block in enumerate(blocks):
        col = i + 2
        cell = ws.cell(row=1, column=col, value=block)
        cell.font = HEADER_FONT
        cell.border = THIN_BORDER
        cell.alignment = Alignment(horizontal='center')
        if SYNERGY_BLOCKS[block]['Type'] == 'Business':
            cell.fill = HEADER_FILL_ORANGE
        else:
            cell.fill = HEADER_FILL_BLUE

    bvi_col = len(blocks) + 2
    thi_col = len(blocks) + 3
    rec_col = len(blocks) + 4

    for col, label, fill in [(bvi_col, 'BVI', HEADER_FILL_ORANGE),
                              (thi_col, 'THI', HEADER_FILL_BLUE),
                              (rec_col, 'Recommendation', HEADER_FILL_DARK)]:
        cell = ws.cell(row=1, column=col, value=label)
        cell.font = HEADER_FONT
        cell.fill = fill
        cell.border = THIN_BORDER
        cell.alignment = Alignment(horizontal='center')

    # Row 2: Weights
    ws.cell(row=2, column=1, value="Weight").font = Font(name='Calibri', size=9, italic=True, color='666666')
    for i, block in enumerate(blocks):
        w = custom_weights.get(block, SYNERGY_BLOCKS[block]['Weight'])
        cell = ws.cell(row=2, column=i + 2, value=f"{w}%")
        cell.font = Font(name='Calibri', size=9, italic=True, color='666666')
        cell.alignment = Alignment(horizontal='center')

    # Freeze panes
    ws.freeze_panes = 'B4'

    # Data rows
    for row_idx, app in enumerate(apps_data, start=3):
        # App name
        cell = ws.cell(row=row_idx, column=1, value=app['name'])
        cell.font = Font(name='Calibri', size=10, bold=True)
        cell.border = THIN_BORDER

        # Block scores
        for i, block in enumerate(blocks):
            score = app['scores'].get(block, 0)
            cell = ws.cell(row=row_idx, column=i + 2, value=score)
            cell.font = CONTENT_FONT
            cell.border = THIN_BORDER
            cell.alignment = Alignment(horizontal='center')
            # Conditional coloring
            if score <= 2:
                cell.fill = PatternFill(start_color='FFC7CE', end_color='FFC7CE', fill_type='solid')
            elif score == 3:
                cell.fill = PatternFill(start_color='FFEB9C', end_color='FFEB9C', fill_type='solid')
            elif score >= 4:
                cell.fill = PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid')

        # BVI, THI
        cell = ws.cell(row=row_idx, column=bvi_col, value=app['bvi'])
        cell.font = Font(name='Calibri', size=10, bold=True)
        cell.border = THIN_BORDER
        cell.alignment = Alignment(horizontal='center')
        cell.number_format = '0.0'

        cell = ws.cell(row=row_idx, column=thi_col, value=app['thi'])
        cell.font = Font(name='Calibri', size=10, bold=True)
        cell.border = THIN_BORDER
        cell.alignment = Alignment(horizontal='center')
        cell.number_format = '0.0'

        # Recommendation
        rec = app['recommendation']
        cell = ws.cell(row=row_idx, column=rec_col, value=rec)
        cell.font = Font(name='Calibri', size=10, bold=True, color=REC_COLORS.get(rec, {}).get('font', '000000'))
        cell.fill = PatternFill(start_color=REC_COLORS.get(rec, {}).get('fill', 'FFFFFF'),
                                end_color=REC_COLORS.get(rec, {}).get('fill', 'FFFFFF'), fill_type='solid')
        cell.border = THIN_BORDER
        cell.alignment = Alignment(horizontal='center')

    return ws


def build_dashboard_sheet(wb, apps_data):
    """Build the Dashboard sheet with scatter chart."""
    ws = wb.create_sheet("Dashboard")

    # Data table for chart (hidden reference)
    ws.cell(row=1, column=1, value="Application").font = Font(name='Calibri', size=9, color='999999')
    ws.cell(row=1, column=2, value="THI").font = Font(name='Calibri', size=9, color='999999')
    ws.cell(row=1, column=3, value="BVI").font = Font(name='Calibri', size=9, color='999999')
    ws.cell(row=1, column=4, value="Recommendation").font = Font(name='Calibri', size=9, color='999999')

    for i, app in enumerate(apps_data, start=2):
        ws.cell(row=i, column=1, value=app['name'])
        ws.cell(row=i, column=2, value=app['thi'])
        ws.cell(row=i, column=3, value=app['bvi'])
        ws.cell(row=i, column=4, value=app['recommendation'])

    n = len(apps_data)

    # Quadrant reference lines
    line_start = n + 4
    ws.cell(row=line_start, column=1, value="H-Line")
    ws.cell(row=line_start, column=2, value=0)
    ws.cell(row=line_start, column=3, value=60)
    ws.cell(row=line_start + 1, column=2, value=100)
    ws.cell(row=line_start + 1, column=3, value=60)
    ws.cell(row=line_start + 2, column=1, value="V-Line")
    ws.cell(row=line_start + 2, column=2, value=60)
    ws.cell(row=line_start + 2, column=3, value=0)
    ws.cell(row=line_start + 3, column=2, value=60)
    ws.cell(row=line_start + 3, column=3, value=100)

    # Create scatter chart
    chart = ScatterChart()
    chart.title = "Application Portfolio - Strategic Positioning"
    chart.x_axis.title = "Technical Health Index (THI)"
    chart.y_axis.title = "Business Value Index (BVI)"
    chart.x_axis.scaling.min = 0
    chart.x_axis.scaling.max = 100
    chart.y_axis.scaling.min = 0
    chart.y_axis.scaling.max = 100
    chart.width = 35
    chart.height = 22
    chart.style = 2

    # Group apps by recommendation for coloring
    rec_groups = {}
    for i, app in enumerate(apps_data):
        rec = app['recommendation']
        if rec not in rec_groups:
            rec_groups[rec] = []
        rec_groups[rec].append(i + 2)  # row number (1-indexed, header at 1)

    marker_colors = {
        'EVOLVE': '00B050',
        'INVEST': 'FFC000',
        'MAINTAIN': '4472C4',
        'ELIMINATE': 'FF0000',
    }

    for rec, rows in rec_groups.items():
        for row in rows:
            x_vals = Reference(ws, min_col=2, min_row=row, max_row=row)
            y_vals = Reference(ws, min_col=3, min_row=row, max_row=row)
            series = Series(y_vals, x_vals, title=ws.cell(row=row, column=1).value)
            series.marker = Marker(symbol='circle', size=8)
            color = marker_colors.get(rec, '999999')
            series.marker.graphicalProperties.solidFill = color
            series.graphicalProperties.line.noFill = True
            chart.series.append(series)

    # Horizontal reference line at BVI=60
    h_x = Reference(ws, min_col=2, min_row=line_start, max_row=line_start + 1)
    h_y = Reference(ws, min_col=3, min_row=line_start, max_row=line_start + 1)
    h_series = Series(h_y, h_x, title="Threshold")
    h_series.graphicalProperties.line.solidFill = '000000'
    h_series.graphicalProperties.line.dashStyle = 'dash'
    h_series.graphicalProperties.line.width = 15000
    h_series.marker = Marker(symbol='none')
    chart.series.append(h_series)

    # Vertical reference line at THI=60
    v_x = Reference(ws, min_col=2, min_row=line_start + 2, max_row=line_start + 3)
    v_y = Reference(ws, min_col=3, min_row=line_start + 2, max_row=line_start + 3)
    v_series = Series(v_y, v_x, title=None)
    v_series.graphicalProperties.line.solidFill = '000000'
    v_series.graphicalProperties.line.dashStyle = 'dash'
    v_series.graphicalProperties.line.width = 15000
    v_series.marker = Marker(symbol='none')
    chart.series.append(v_series)

    ws.add_chart(chart, "A" + str(n + 8))

    # Quadrant labels
    ws.cell(row=n + 6, column=1, value="Legend:").font = Font(bold=True)
    for idx, (rec, color_info) in enumerate(REC_COLORS.items()):
        cell = ws.cell(row=n + 7 + idx, column=1, value=rec)
        cell.fill = PatternFill(start_color=color_info['fill'], end_color=color_info['fill'], fill_type='solid')
        cell.font = Font(name='Calibri', size=10, bold=True, color=color_info['font'])

    return ws


def build_roadmap_sheet(wb, apps_data):
    """Build the Strategic Roadmap sheet."""
    ws = wb.create_sheet("Strategic Roadmap")

    headers = ['Application Name', 'BVI', 'THI', 'Recommendation', 'Subcategory', 'Quick Win?', 'Priority', 'Rationale', 'Comments']
    widths = [35, 15, 15, 18, 18, 12, 18, 25, 30]

    for i, (header, width) in enumerate(zip(headers, widths), start=1):
        cell = ws.cell(row=1, column=i, value=header)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL_DARK
        cell.border = THIN_BORDER
        cell.alignment = Alignment(horizontal='center')
        ws.column_dimensions[get_column_letter(i)].width = width

    ws.freeze_panes = 'A2'

    for row_idx, app in enumerate(apps_data, start=2):
        rec = app['recommendation']
        rec_colors = REC_COLORS.get(rec, {'fill': 'FFFFFF', 'font': '000000'})

        # App name
        cell = ws.cell(row=row_idx, column=1, value=app['name'])
        cell.font = Font(name='Calibri', size=10, bold=True)
        cell.border = THIN_BORDER

        # BVI
        cell = ws.cell(row=row_idx, column=2, value=app['bvi'])
        cell.font = CONTENT_FONT
        cell.border = THIN_BORDER
        cell.alignment = Alignment(horizontal='center')
        cell.number_format = '0.0'

        # THI
        cell = ws.cell(row=row_idx, column=3, value=app['thi'])
        cell.font = CONTENT_FONT
        cell.border = THIN_BORDER
        cell.alignment = Alignment(horizontal='center')
        cell.number_format = '0.0'

        # Recommendation
        cell = ws.cell(row=row_idx, column=4, value=rec)
        cell.font = Font(name='Calibri', size=10, bold=True, color=rec_colors['font'])
        cell.fill = PatternFill(start_color=rec_colors['fill'], end_color=rec_colors['fill'], fill_type='solid')
        cell.border = THIN_BORDER
        cell.alignment = Alignment(horizontal='center')

        # Subcategory
        cell = ws.cell(row=row_idx, column=5, value=app.get('subcategory', ''))
        cell.font = CONTENT_FONT
        cell.border = THIN_BORDER
        cell.alignment = Alignment(horizontal='center')

        # Quick Win
        cell = ws.cell(row=row_idx, column=6, value='Yes' if app.get('quick_win') else 'No')
        cell.font = CONTENT_FONT
        cell.border = THIN_BORDER
        cell.alignment = Alignment(horizontal='center')

        # Priority
        priority = app.get('priority', '')
        cell = ws.cell(row=row_idx, column=7, value=priority)
        cell.font = Font(name='Calibri', size=10, bold=True)
        cell.border = THIN_BORDER
        cell.alignment = Alignment(horizontal='center')

        # Rationale - lookup from matrix
        rationale = ''
        for decision, subcat, prio, rat in MATRIX_CONFIG:
            if decision == rec and subcat == app.get('subcategory', ''):
                rationale = rat
                break
        cell = ws.cell(row=row_idx, column=8, value=rationale)
        cell.font = CONTENT_FONT
        cell.border = THIN_BORDER

        # Comments
        cell = ws.cell(row=row_idx, column=9, value='')
        cell.font = CONTENT_FONT
        cell.border = THIN_BORDER

    return ws


def build_app_groups_sheet(wb, apps_data):
    """Build the Application Groups sheet."""
    ws = wb.create_sheet("Application Groups")

    # Group apps
    groups = {cat: [] for cat in APP_GROUP_CATEGORIES}
    groups['Uncategorized'] = []

    for app in apps_data:
        qa_texts = [a for a in app.get('qa_answers', {}).values() if a]
        cat = categorize_app(app['name'], qa_texts)
        groups[cat].append(app)

    # Layout: 2 rows x 3 cols grid
    positions = [
        ('Task Management / User Alignment', 3, 2),
        ('Maintenance & Asset Mgmt', 3, 7),
        ('Grid Operations / Engineering', 3, 12),
        ('Document / Info Management', 25, 2),
        ('Corporate / Administrative', 25, 7),
        ('Uncategorized', 25, 12),
    ]

    # Title
    ws.merge_cells('B1:P1')
    cell = ws.cell(row=1, column=2, value="APPLICATION GROUPS - Functional Categorization")
    cell.font = Font(name='Calibri', size=14, bold=True, color='333333')
    cell.alignment = Alignment(horizontal='center')

    for cat_name, start_row, start_col in positions:
        color = APP_GROUP_CATEGORIES.get(cat_name, {}).get('color', '999999')
        apps_in_cat = groups.get(cat_name, [])

        # Header
        end_col = start_col + 3
        ws.merge_cells(start_row=start_row, start_column=start_col, end_row=start_row, end_column=end_col)
        cell = ws.cell(row=start_row, column=start_col, value=cat_name)
        cell.font = Font(name='Calibri', size=12, bold=True, color='FFFFFF')
        cell.fill = PatternFill(start_color=color, end_color=color, fill_type='solid')
        cell.alignment = Alignment(horizontal='center')
        cell.border = THIN_BORDER

        # App items
        for i, app in enumerate(apps_in_cat[:15]):
            row = start_row + 1 + i
            ws.merge_cells(start_row=row, start_column=start_col, end_row=row, end_column=end_col)
            cell = ws.cell(row=row, column=start_col, value=app['name'])
            cell.font = Font(name='Calibri', size=10)
            rec = app.get('recommendation', '')
            rec_colors = REC_COLORS.get(rec, {'fill': 'F2F2F2'})
            cell.fill = PatternFill(start_color=rec_colors['fill'], end_color=rec_colors['fill'], fill_type='solid')
            cell.border = THIN_BORDER

    # Column widths
    for col in [2, 7, 12]:
        for offset in range(4):
            ws.column_dimensions[get_column_letter(col + offset)].width = 10

    return ws


def build_value_chain_sheet(wb, apps_data):
    """Build the Value Chain sheet."""
    ws = wb.create_sheet("Value Chain")

    # Title
    ws.merge_cells('B2:T2')
    cell = ws.cell(row=2, column=2, value="AVANGRID INTEGRATED UTILITY VALUE CHAIN")
    cell.font = Font(name='Calibri', size=14, bold=True, color='FFFFFF')
    cell.fill = PatternFill(start_color='000000', end_color='000000', fill_type='solid')
    cell.alignment = Alignment(horizontal='center')

    # Group apps
    stages = {s: [] for s in VALUE_CHAIN_STAGES}
    stages['Cross-Cutting'] = []

    for app in apps_data:
        qa_texts = [a for a in app.get('qa_answers', {}).values() if a]
        stage = categorize_value_chain(app['name'], qa_texts)
        stages[stage].append(app)

    stage_positions = [
        ('Generation (Renewables)', 4, 2),
        ('Transmission (Transport)', 4, 7),
        ('Distribution (Delivery)', 4, 12),
        ('Customer Solutions', 4, 17),
        ('Corporate / Shared Services', 20, 2),
        ('Cross-Cutting', 20, 12),
    ]

    for stage_name, start_row, start_col in stage_positions:
        color = VALUE_CHAIN_STAGES.get(stage_name, {}).get('color', '999999')
        apps_in_stage = stages.get(stage_name, [])
        end_col = start_col + 3

        # Header
        ws.merge_cells(start_row=start_row, start_column=start_col, end_row=start_row, end_column=end_col)
        cell = ws.cell(row=start_row, column=start_col, value=stage_name)
        cell.font = Font(name='Calibri', size=11, bold=True, color='FFFFFF')
        cell.fill = PatternFill(start_color=color, end_color=color, fill_type='solid')
        cell.alignment = Alignment(horizontal='center')
        cell.border = THIN_BORDER

        for i, app in enumerate(apps_in_stage[:12]):
            row = start_row + 1 + i
            ws.merge_cells(start_row=row, start_column=start_col, end_row=row, end_column=end_col)
            cell = ws.cell(row=row, column=start_col, value=app['name'])
            cell.font = Font(name='Calibri', size=10)
            rec = app.get('recommendation', '')
            rec_colors = REC_COLORS.get(rec, {'fill': 'F2F2F2'})
            cell.fill = PatternFill(start_color=rec_colors['fill'], end_color=rec_colors['fill'], fill_type='solid')
            cell.border = THIN_BORDER
            cell.alignment = Alignment(horizontal='center')

    # Arrows between stages (row 4)
    for arrow_col in [6, 11, 16]:
        cell = ws.cell(row=4, column=arrow_col, value="\u27A1")
        cell.font = Font(name='Calibri', size=16)
        cell.alignment = Alignment(horizontal='center', vertical='center')

    return ws


def build_app_sheet(wb, app_data, session):
    """Build an individual application assessment sheet."""
    sheet_name = sanitize_sheet_name(app_data['name'])
    ws = wb.create_sheet(sheet_name)

    ws.column_dimensions['A'].width = 50
    ws.column_dimensions['B'].width = 80

    # Title
    ws.merge_cells('A1:B1')
    cell = ws.cell(row=1, column=1, value=f"Assessment: {app_data['name']}")
    cell.font = Font(name='Calibri', size=14, bold=True, color='E87722')

    # Scorecard header
    ws.cell(row=3, column=1, value="EXECUTIVE SCORECARD").font = HEADER_FONT
    ws['A3'].fill = HEADER_FILL_DARK
    ws['A3'].border = THIN_BORDER
    ws.cell(row=3, column=2, value="SCORE (0-5)").font = HEADER_FONT
    ws['B3'].fill = HEADER_FILL_DARK
    ws['B3'].border = THIN_BORDER

    # Score rows
    blocks = list(SYNERGY_BLOCKS.keys())
    for i, block in enumerate(blocks, start=4):
        cell_a = ws.cell(row=i, column=1, value=block)
        cell_a.font = Font(name='Calibri', size=10, bold=True)
        cell_a.fill = CONTENT_FILL
        cell_a.border = THIN_BORDER
        cell_a.alignment = Alignment(horizontal='right')

        score = app_data['scores'].get(block, 0)
        cell_b = ws.cell(row=i, column=2, value=score)
        cell_b.font = Font(name='Calibri', size=11)
        cell_b.border = THIN_BORDER
        cell_b.alignment = Alignment(horizontal='center')
        # Add dropdown validation
        dv = DataValidation(type="whole", operator="between", formula1="0", formula2="5")
        ws.add_data_validation(dv)
        dv.add(cell_b)

    # Detailed Q&A sections
    current_row = 14

    # Get all Q&A data from all sources
    qa_answers = session.query(QuestionnaireAnswer).filter_by(application_id=app_data['id']).all()
    ta_answers = session.query(TranscriptAnswer).filter_by(application_id=app_data['id']).all()
    david_notes = session.query(DavidNote).filter_by(application_id=app_data['id'], note_type='answer').all()

    # Build Q&A dict per block (merge all sources)
    for block in blocks:
        # Block header
        ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=2)
        cell = ws.cell(row=current_row, column=1, value=block.upper())
        cell.font = Font(name='Calibri', size=11, bold=True, color='FFFFFF')
        cell.fill = PatternFill(start_color='444444', end_color='444444', fill_type='solid')
        cell.border = THIN_BORDER
        current_row += 1

        # Definitions
        cell = ws.cell(row=current_row, column=1, value="Definitions")
        cell.font = Font(name='Calibri', size=10, bold=True)
        current_row += 1

        for score_val, definition in BLOCK_DEFINITIONS.get(block, {}).items():
            cell = ws.cell(row=current_row, column=1, value=f"{score_val} - {definition}")
            cell.font = Font(name='Calibri', size=9, color='666666')
            current_row += 1

        current_row += 1

        # Q&A header
        ws.cell(row=current_row, column=1, value="Q").font = HEADER_FONT
        ws['A' + str(current_row)].fill = HEADER_FILL_DARK
        ws['A' + str(current_row)].border = THIN_BORDER
        ws.cell(row=current_row, column=2, value="A").font = HEADER_FONT
        ws['B' + str(current_row)].fill = HEADER_FILL_DARK
        ws['B' + str(current_row)].border = THIN_BORDER
        current_row += 1

        # Collect Q&A for this block
        block_qa = {}
        for qa in qa_answers:
            if qa.synergy_block == block:
                block_qa[qa.question_text] = qa.answer_text or '-'
        for ta in ta_answers:
            if ta.synergy_block == block and ta.answer_text:
                block_qa[ta.question_text] = ta.answer_text
        for dn in david_notes:
            if dn.synergy_block == block and dn.answer_text:
                block_qa[dn.question_text] = dn.answer_text

        if block_qa:
            for question, answer in block_qa.items():
                cell_q = ws.cell(row=current_row, column=1, value=question)
                cell_q.font = Font(name='Calibri', size=9)
                cell_q.fill = CONTENT_FILL
                cell_q.border = THIN_BORDER
                cell_q.alignment = WRAP_ALIGN

                cell_a = ws.cell(row=current_row, column=2, value=answer)
                cell_a.font = Font(name='Calibri', size=9)
                cell_a.fill = CONTENT_FILL
                cell_a.border = THIN_BORDER
                cell_a.alignment = WRAP_ALIGN
                current_row += 1
        else:
            cell = ws.cell(row=current_row, column=1, value="No data available")
            cell.font = Font(name='Calibri', size=9, italic=True, color='999999')
            current_row += 1

        current_row += 1  # Blank separator

    # Tab color based on recommendation
    rec = app_data.get('recommendation', '')
    if rec == 'EVOLVE':
        ws.sheet_properties.tabColor = '00B050'
    elif rec == 'INVEST':
        ws.sheet_properties.tabColor = 'FFC000'
    elif rec == 'MAINTAIN':
        ws.sheet_properties.tabColor = '4472C4'
    elif rec == 'ELIMINATE':
        ws.sheet_properties.tabColor = 'FF0000'
    else:
        ws.sheet_properties.tabColor = 'D9D9D9'

    return ws


# ============================================================
# Main generation function
# ============================================================

def generate_portfolio_excel(custom_weights=None):
    """Generate the full portfolio Excel workbook.
    Returns bytes of the generated .xlsx file."""

    session = get_session()
    try:
        apps = session.query(Application).order_by(Application.name).all()
        if not apps:
            return None

        # Build apps_data list
        apps_data = []
        for app in apps:
            scores_data = session.query(SynergyScore).filter_by(
                application_id=app.id, approved=True
            ).all()

            scores = {s.block_name: s.score for s in scores_data}

            # Use custom weights
            w = custom_weights or {b: SYNERGY_BLOCKS[b]['Weight'] for b in SYNERGY_BLOCKS}
            weight_dict = {b: {'Weight': w.get(b, SYNERGY_BLOCKS[b]['Weight'])} for b in SYNERGY_BLOCKS}
            bvi, thi = calculate_bvi_thi(scores, weight_dict)
            rec = get_recommendation(bvi, thi)

            # Priority
            priority = ''
            if app.subcategory:
                priority_map = {m[1]: m[2] for m in MATRIX_CONFIG if m[0] == rec}
                base_priority = priority_map.get(app.subcategory, '')
                if not base_priority:
                    # Fallback: check all matrix entries
                    for decision, subcat, prio, rat in MATRIX_CONFIG:
                        if subcat == app.subcategory:
                            base_priority = prio
                            break
                if app.quick_win and base_priority.startswith('P2'):
                    priority = 'P1 - Quick Win'
                elif app.quick_win and base_priority.startswith('P3'):
                    priority = 'P2 - Quick Win'
                else:
                    priority = base_priority

            # Collect Q&A answers for grouping
            qa_answers = session.query(QuestionnaireAnswer).filter_by(application_id=app.id).all()
            qa_dict = {}
            for qa in qa_answers:
                if qa.answer_text:
                    qa_dict[qa.question_text] = qa.answer_text

            apps_data.append({
                'id': app.id,
                'name': app.name,
                'scores': scores,
                'bvi': bvi,
                'thi': thi,
                'recommendation': rec,
                'subcategory': app.subcategory or '',
                'quick_win': app.quick_win,
                'priority': priority,
                'qa_answers': qa_dict,
            })

        # Create workbook
        wb = Workbook()
        # Remove default sheet
        wb.remove(wb.active)

        # Build sheets
        build_calculator_sheet(wb, apps_data, custom_weights or {b: SYNERGY_BLOCKS[b]['Weight'] for b in SYNERGY_BLOCKS})
        build_dashboard_sheet(wb, apps_data)
        build_roadmap_sheet(wb, apps_data)
        build_app_groups_sheet(wb, apps_data)
        build_value_chain_sheet(wb, apps_data)

        # Individual app sheets
        for app in apps_data:
            build_app_sheet(wb, app, session)

        # Save to bytes
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return buffer.getvalue()

    finally:
        close_session(session)
