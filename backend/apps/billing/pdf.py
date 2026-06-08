"""
PDF invoice generator using ReportLab.
Returns a BytesIO buffer ready for FileResponse streaming.
"""
import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
)

# Brand palette
PRIMARY = colors.HexColor('#1e3a5f')
ACCENT = colors.HexColor('#2563eb')
LIGHT_BG = colors.HexColor('#f0f4ff')
GREY = colors.HexColor('#6b7280')
BLACK = colors.black
WHITE = colors.white


def generate_invoice_pdf(invoice) -> io.BytesIO:
    """Generate a GST-compliant invoice PDF and return the buffer."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=20 * mm,
    )
    story = []

    # ── Header ────────────────────────────────────────────────
    header_data = [[
        Paragraph(
            '<font color="#1e3a5f"><b>CoWorkHub</b></font><br/>'
            '<font size="8" color="#6b7280">Smart Coworking Space Management</font>',
            ParagraphStyle('hdr', fontName='Helvetica-Bold', fontSize=18, leading=22),
        ),
        Paragraph(
            f'<font color="#2563eb"><b>TAX INVOICE</b></font><br/>'
            f'<font size="9" color="#374151">{invoice.invoice_number}</font>',
            ParagraphStyle('invno', fontName='Helvetica-Bold', fontSize=16,
                           alignment=2, leading=20),
        ),
    ]]
    header_tbl = Table(header_data, colWidths=[95 * mm, 85 * mm])
    header_tbl.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(header_tbl)
    story.append(HRFlowable(width='100%', thickness=1.5, color=PRIMARY, spaceAfter=6))

    # ── Bill To / Invoice Details ──────────────────────────────
    company = invoice.company
    bill_to = (
        f'<b>Bill To:</b><br/>'
        f'<b>{company.name}</b><br/>'
        f'{company.address or ""}<br/>'
        f'{company.city}, {company.state} — {company.pincode}<br/>'
        f'GST: {company.gst_number or "N/A"}  |  PAN: {company.pan_number or "N/A"}'
    )
    inv_details = (
        f'<b>Invoice Date:</b> {invoice.created_at.strftime("%d %b %Y")}<br/>'
        f'<b>Period:</b> {invoice.billing_period_start.strftime("%d %b")} – '
        f'{invoice.billing_period_end.strftime("%d %b %Y")}<br/>'
        f'<b>Due Date:</b> {invoice.due_date.strftime("%d %b %Y") if invoice.due_date else "On receipt"}<br/>'
        f'<b>Status:</b> {invoice.get_status_display()}'
    )
    meta_data = [[
        Paragraph(bill_to, ParagraphStyle('bt', fontName='Helvetica', fontSize=9, leading=13)),
        Paragraph(inv_details, ParagraphStyle('id', fontName='Helvetica', fontSize=9,
                                              leading=13, alignment=2)),
    ]]
    meta_tbl = Table(meta_data, colWidths=[95 * mm, 85 * mm])
    meta_tbl.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BG),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (0, -1), 8),
        ('RIGHTPADDING', (-1, 0), (-1, -1), 8),
        ('ROUNDEDCORNERS', [4]),
    ]))
    story.append(meta_tbl)
    story.append(Spacer(1, 6 * mm))

    # ── Line Items Table ───────────────────────────────────────
    col_widths = [100 * mm, 15 * mm, 25 * mm, 30 * mm]
    th = ParagraphStyle('th', fontName='Helvetica-Bold', fontSize=9, textColor=WHITE)
    td = ParagraphStyle('td', fontName='Helvetica', fontSize=9, leading=12)

    rows = [[
        Paragraph('Description', th),
        Paragraph('Qty', th),
        Paragraph('Rate (Rs)', th),
        Paragraph('Amount (Rs)', th),
    ]]
    for item in invoice.line_items:
        rows.append([
            Paragraph(str(item.get('description', '')), td),
            Paragraph(str(item.get('qty', 1)), td),
            Paragraph(f'{float(item.get("rate", 0)):,.2f}', td),
            Paragraph(f'{float(item.get("amount", 0)):,.2f}', td),
        ])

    items_tbl = Table(rows, colWidths=col_widths, repeatRows=1)
    items_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, LIGHT_BG]),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#d1d5db')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (0, -1), 6),
    ]))
    story.append(items_tbl)
    story.append(Spacer(1, 4 * mm))

    # ── Totals ─────────────────────────────────────────────────
    def money(val):
        return f'Rs {float(val):,.2f}'

    totals_data = []
    totals_data.append(['Subtotal', money(invoice.subtotal)])
    if invoice.cgst_amount:
        totals_data.append([f'CGST @ {invoice.cgst_rate}%', money(invoice.cgst_amount)])
    if invoice.sgst_amount:
        totals_data.append([f'SGST @ {invoice.sgst_rate}%', money(invoice.sgst_amount)])
    if invoice.igst_amount:
        totals_data.append([f'IGST @ {invoice.igst_rate}%', money(invoice.igst_amount)])
    totals_data.append(['TOTAL', money(invoice.total_amount)])

    formatted = []
    for i, row in enumerate(totals_data):
        is_total = (i == len(totals_data) - 1)
        fn = 'Helvetica-Bold' if is_total else 'Helvetica'
        fs = 10 if is_total else 9
        formatted.append([
            Paragraph(f'<b>{row[0]}</b>' if is_total else row[0],
                      ParagraphStyle(f'r{i}', fontName=fn, fontSize=fs)),
            Paragraph(f'<b>{row[1]}</b>' if is_total else row[1],
                      ParagraphStyle(f'rv{i}', fontName=fn, fontSize=fs, alignment=2)),
        ])

    totals_tbl = Table(formatted, colWidths=[130 * mm, 40 * mm])
    totals_style_cmds = TableStyle([
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LINEABOVE', (0, -1), (-1, -1), 1.5, PRIMARY),
        ('BACKGROUND', (0, -1), (-1, -1), LIGHT_BG),
    ])
    totals_tbl.setStyle(totals_style_cmds)
    story.append(totals_tbl)
    story.append(Spacer(1, 8 * mm))

    # ── UPI QR Code ────────────────────────────────────────────
    try:
        import qrcode
        upi_string = (
            f'upi://pay?pa=coworkhub@upi&pn=CoWorkHub&'
            f'am={invoice.total_amount}&tn={invoice.invoice_number}&cu=INR'
        )
        qr = qrcode.QRCode(box_size=3, border=2)
        qr.add_data(upi_string)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color='black', back_color='white')

        qr_buf = io.BytesIO()
        qr_img.save(qr_buf, format='PNG')
        qr_buf.seek(0)

        from reportlab.platypus import Image as RLImage
        qr_rl = RLImage(qr_buf, width=28 * mm, height=28 * mm)

        qr_data = [[
            qr_rl,
            Paragraph(
                '<b>Pay via UPI</b><br/>'
                '<font size="8" color="#6b7280">Scan QR or use UPI ID: coworkhub@upi<br/>'
                f'Amount: Rs {invoice.total_amount}</font>',
                ParagraphStyle('qrtxt', fontName='Helvetica', fontSize=9, leading=13),
            ),
        ]]
        qr_tbl = Table(qr_data, colWidths=[35 * mm, 145 * mm])
        qr_tbl.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BG),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (0, -1), 6),
        ]))
        story.append(qr_tbl)
        story.append(Spacer(1, 6 * mm))
    except ImportError:
        pass  # qrcode not installed — skip QR block

    # ── Footer ─────────────────────────────────────────────────
    story.append(HRFlowable(width='100%', thickness=0.5, color=GREY, spaceBefore=4))
    story.append(Paragraph(
        '<font size="8" color="#6b7280">This is a computer-generated invoice. '
        'No signature required. | CoWorkHub — Sanchi Connect</font>',
        ParagraphStyle('footer', fontName='Helvetica', fontSize=8,
                       textColor=GREY, alignment=1),
    ))

    if invoice.notes:
        story.append(Spacer(1, 3 * mm))
        story.append(Paragraph(
            f'<b>Notes:</b> {invoice.notes}',
            ParagraphStyle('notes', fontName='Helvetica', fontSize=8, textColor=GREY),
        ))

    doc.build(story)
    buf.seek(0)
    return buf
