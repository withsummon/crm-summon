import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def run():
	from crm.demo.samples.generate_sample import ROWS

	output_dir = os.path.dirname(os.path.abspath(__file__))
	pdf_path = os.path.join(output_dir, "financial_spread_sample.pdf")

	doc = SimpleDocTemplate(
		pdf_path,
		pagesize=A4,
		rightMargin=36,
		leftMargin=36,
		topMargin=36,
		bottomMargin=36
	)
	story = []

	styles = getSampleStyleSheet()

	# Custom Styles
	title_style = ParagraphStyle(
		'DocTitle',
		parent=styles['Heading1'],
		fontName='Helvetica-Bold',
		fontSize=18,
		textColor=colors.HexColor('#0d9488'),
		spaceAfter=4
	)
	
	subtitle_style = ParagraphStyle(
		'DocSubtitle',
		parent=styles['Normal'],
		fontName='Helvetica-Bold',
		fontSize=12,
		textColor=colors.HexColor('#1e293b'),
		spaceAfter=2
	)

	meta_style = ParagraphStyle(
		'DocMeta',
		parent=styles['Normal'],
		fontName='Helvetica',
		fontSize=9,
		textColor=colors.HexColor('#64748b'),
		spaceAfter=15
	)

	cell_style = ParagraphStyle(
		'Cell',
		parent=styles['Normal'],
		fontName='Helvetica',
		fontSize=9,
		textColor=colors.HexColor('#334155')
	)

	cell_bold_style = ParagraphStyle(
		'CellBold',
		parent=styles['Normal'],
		fontName='Helvetica-Bold',
		fontSize=9,
		textColor=colors.HexColor('#1e293b')
	)

	header_style = ParagraphStyle(
		'HeaderCell',
		parent=styles['Normal'],
		fontName='Helvetica-Bold',
		fontSize=9,
		textColor=colors.white
	)

	# Add Header elements
	story.append(Paragraph("BNI CRM ENTERPRISE", subtitle_style))
	story.append(Paragraph("Financial Spreading Statement (PSAK Format)", title_style))
	story.append(Paragraph("Classification: INTERNAL USE ONLY &bull; Prepared for Credit Analysis RAG Extract Validation", meta_style))
	story.append(Spacer(1, 10))

	# Construct Table
	table_data = [[
		Paragraph("Statement Type", header_style),
		Paragraph("Line Item Description", header_style),
		Paragraph("Year", header_style),
		Paragraph("Amount (IDR)", header_style)
	]]

	for idx, row in enumerate(ROWS):
		st_type, label, year, amount = row
		formatted_amount = "{:,.0f}".format(amount).replace(",", ".")
		
		table_data.append([
			Paragraph(st_type, cell_bold_style),
			Paragraph(label, cell_style),
			Paragraph(str(year), cell_style),
			Paragraph(formatted_amount, cell_bold_style)
		])

	# Create Table widget
	# Column widths: Statement Type (100), Line Item (200), Year (60), Amount (160)
	t = Table(table_data, colWidths=[100, 210, 60, 150])
	
	# Design styling matching BNI Teal Theme
	t_style = TableStyle([
		('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d9488')),
		('ALIGN', (0, 0), (-1, -1), 'LEFT'),
		('ALIGN', (3, 0), (3, -1), 'RIGHT'), # right-align amounts
		('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
		('TOPPADDING', (0, 0), (-1, -1), 6),
		('BOTTOMPADDING', (0, 0), (-1, -1), 6),
		('LEFTPADDING', (0, 0), (-1, -1), 10),
		('RIGHTPADDING', (0, 0), (-1, -1), 10),
		('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
	])

	# Add alternating row background colors
	for i in range(1, len(table_data)):
		bg_color = colors.HexColor('#f8fafc') if i % 2 == 0 else colors.white
		t_style.add('BACKGROUND', (0, i), (-1, i), bg_color)

	t.setStyle(t_style)
	story.append(t)
	
	story.append(Spacer(1, 20))
	footer_style = ParagraphStyle(
		'FooterText',
		parent=styles['Normal'],
		fontName='Helvetica-Oblique',
		fontSize=8,
		textColor=colors.HexColor('#94a3b8'),
		alignment=1 # Center align
	)
	story.append(Paragraph("This PDF report serves as a secure mock statement for checking automated financial spreading and ratio calculations in BNI CRM.", footer_style))

	doc.build(story)
	print(f"Successfully generated PDF: {pdf_path} ({os.path.getsize(pdf_path)} bytes)")

if __name__ == "__main__":
	run()
