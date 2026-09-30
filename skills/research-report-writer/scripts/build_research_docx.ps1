<#
.SYNOPSIS
  Build a Thai undergraduate research report (5-chapter thesis / เล่มวิจัย) as a real
  .docx via Word COM automation, from a tagged UTF-8 text file. See ../SKILL.md and
  ../references/tag-format.md for the full tag reference.

.DESCRIPTION
  Produces: cover section with no page numbers, front matter numbered ก ข ค (Thai
  letters), body numbered 1 2 3 restarting at บทที่ 1, page numbers top-right,
  auto-updating สารบัญ / สารบัญตาราง / สารบัญภาพ (Word TOC fields), real Word tables,
  pictures, captions, APA hanging-indent references.

  Prints PAGES=<n> (total rendered pages, computed by Word) on success.
#>
param(
    [Parameter(Mandatory=$true)][string]$InputPath,
    [Parameter(Mandatory=$true)][string]$OutputPath,
    [string]$PdfPath = "",
    [string]$FontName = "TH Sarabun New",
    [int]$FontSize = 16,
    [int]$HeadingSize = 20,
    [double]$MarginTopIn = 1.5,
    [double]$MarginLeftIn = 1.5,
    [double]$MarginRightIn = 1.0,
    [double]$MarginBottomIn = 1.0,
    [double]$HeaderDistanceIn = 0.8,
    [double]$LineSpacing = 1.0,
    [int]$TocLevels = 2,
    [ValidateSet("right","center")][string]$PageNumAlign = "right",
    [ValidateSet("header","footer")][string]$PageNumPlace = "header"
)

$ErrorActionPreference = "Stop"
$InputPath  = (Resolve-Path $InputPath).Path
$OutputPath = [System.IO.Path]::GetFullPath($OutputPath)
$baseDir    = Split-Path $InputPath -Parent

# --- Guard: refuse (rather than kill Word) if the output file is open/locked. ---
if (Test-Path $OutputPath) {
    try { $fs = [System.IO.File]::Open($OutputPath, 'Open', 'ReadWrite', 'None'); $fs.Close() }
    catch { throw "Output file is open in another program (probably Word). Close it and rerun: $OutputPath" }
}

$lines = Get-Content -Path $InputPath -Encoding UTF8

# Style names used by TOC \t switches (kept ASCII so field codes are locale-safe).
$StyFront = "TH Front Heading"
$StyTCap  = "TH Table Caption"
$StyFCap  = "TH Figure Caption"

$word = $null; $doc = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $doc = $word.Documents.Add()
    # Points as [single] - see the NOTE above Reset-Para.
    function InPt([double]$x) { [single]($x * 72.0) }
    function CmPt([double]$x) { [single]($x * 72.0 / 2.54) }

    # Thai is a Complex Script in Word: size/bold/italic must be set on the *Bi
    # properties too or Thai glyphs ignore them. Never use NameFarEast (CJK only;
    # throws 0x800A16D4 on Thai installs).
    function Set-FontProps($f, $size, $bold, $italic = $false) {
        $f.Name = $FontName; $f.NameAscii = $FontName; $f.NameOther = $FontName; $f.NameBi = $FontName
        $f.Size = [single]($size); $f.SizeBi = [single]($size)
        $f.Bold = [int]$bold; $f.BoldBi = [int]$bold
        $f.Italic = [int]$italic; $f.ItalicBi = [int]$italic
        $f.Color = 0
    }

    # --- Styles ------------------------------------------------------------------
    $normal = $doc.Styles.Item(-1)
    Set-FontProps $normal.Font $FontSize $false
    $pf = $normal.ParagraphFormat
    $pf.SpaceBefore = [single](0); $pf.SpaceAfter = [single](0)
    if ($LineSpacing -eq 1.0) { $pf.LineSpacingRule = 0 }          # wdLineSpaceSingle
    elseif ($LineSpacing -eq 1.5) { $pf.LineSpacingRule = 1 }      # wdLineSpace1pt5
    else { $pf.LineSpacingRule = 5; $pf.LineSpacing = [single](12 * $LineSpacing) }   # wdLineSpaceMultiple
    # wdAlignParagraphThaiJustify (9), NOT Justify (3): plain justify stretches the few
    # ASCII spaces in Thai text into huge gaps.
    $pf.Alignment = 9

    $h1 = $doc.Styles.Item(-2); Set-FontProps $h1.Font $HeadingSize $true
    $h1.ParagraphFormat.Alignment = 1; $h1.ParagraphFormat.SpaceBefore = [single](0); $h1.ParagraphFormat.SpaceAfter = [single](18)
    $h1.ParagraphFormat.PageBreakBefore = -1; $h1.ParagraphFormat.KeepWithNext = -1
    $h1.ParagraphFormat.LeftIndent = [single](0); $h1.ParagraphFormat.FirstLineIndent = [single](0)

    $h2 = $doc.Styles.Item(-3); Set-FontProps $h2.Font $FontSize $true
    $h2.ParagraphFormat.Alignment = 0; $h2.ParagraphFormat.SpaceBefore = [single](12); $h2.ParagraphFormat.SpaceAfter = [single](0)
    $h2.ParagraphFormat.KeepWithNext = -1; $h2.ParagraphFormat.LeftIndent = [single](0); $h2.ParagraphFormat.FirstLineIndent = [single](0)

    $h3 = $doc.Styles.Item(-4); Set-FontProps $h3.Font $FontSize $true
    $h3.ParagraphFormat.Alignment = 0; $h3.ParagraphFormat.SpaceBefore = [single](6); $h3.ParagraphFormat.SpaceAfter = [single](0)
    $h3.ParagraphFormat.KeepWithNext = -1; $h3.ParagraphFormat.LeftIndent = [single]((InPt (0.5))); $h3.ParagraphFormat.FirstLineIndent = [single](0)

    function New-ParaStyle($name, $size = $FontSize, $bold = $false) {
        try { $s = $doc.Styles.Item($name) } catch { $s = $doc.Styles.Add($name, 1) }
        $s.BaseStyle = -1; Set-FontProps $s.Font $size $bold
        $s.ParagraphFormat.FirstLineIndent = [single](0); $s.ParagraphFormat.LeftIndent = [single](0)
        $s
    }
    # Every paragraph kind gets its own style so the .docx stays easy to restyle in Word.
    $sf = New-ParaStyle $StyFront $HeadingSize $true
    $sf.ParagraphFormat.Alignment = 1; $sf.ParagraphFormat.PageBreakBefore = -1; $sf.ParagraphFormat.SpaceAfter = [single](18)
    $sf.ParagraphFormat.KeepWithNext = -1

    $st = New-ParaStyle $StyTCap
    $st.ParagraphFormat.Alignment = 0; $st.ParagraphFormat.SpaceBefore = [single](12); $st.ParagraphFormat.SpaceAfter = [single](6)
    $st.ParagraphFormat.KeepWithNext = -1
    # Hanging indent so a wrapped caption lines up under the title text.
    $st.ParagraphFormat.LeftIndent = [single]((CmPt 2.0)); $st.ParagraphFormat.FirstLineIndent = [single](-(CmPt 2.0))

    $sc = New-ParaStyle $StyFCap
    $sc.ParagraphFormat.Alignment = 1; $sc.ParagraphFormat.SpaceBefore = [single](6); $sc.ParagraphFormat.SpaceAfter = [single](12)

    $sb = New-ParaStyle "TH Body"; $sb.ParagraphFormat.Alignment = 9; $sb.ParagraphFormat.FirstLineIndent = [single]((InPt 0.5))
    $sn = New-ParaStyle "TH Body NoIndent"; $sn.ParagraphFormat.Alignment = 9
    foreach ($lvl in 1, 2, 3) {
        $sl = New-ParaStyle "TH List $lvl"; $sl.ParagraphFormat.Alignment = 9
        $sl.ParagraphFormat.LeftIndent = [single]((InPt (0.5 * $lvl + 0.3))); $sl.ParagraphFormat.FirstLineIndent = [single](-(InPt 0.3))
    }
    $sk = New-ParaStyle "TH Keywords"; $sk.ParagraphFormat.Alignment = 9; $sk.ParagraphFormat.SpaceBefore = [single](12)
    $sr = New-ParaStyle "TH Reference"; $sr.ParagraphFormat.Alignment = 0; $sr.ParagraphFormat.SpaceAfter = [single](6)
    $sr.ParagraphFormat.LeftIndent = [single]((InPt 0.5)); $sr.ParagraphFormat.FirstLineIndent = [single](-(InPt 0.5))
    $so = New-ParaStyle "TH Note" ($FontSize - 2); $so.ParagraphFormat.Alignment = 0
    $so.ParagraphFormat.SpaceBefore = [single](3); $so.ParagraphFormat.SpaceAfter = [single](6)
    $sg = New-ParaStyle "TH Figure"; $sg.ParagraphFormat.Alignment = 1; $sg.ParagraphFormat.KeepWithNext = -1
    $sp = New-ParaStyle "TH Plain"; $sp.ParagraphFormat.Alignment = 0
    $sx = New-ParaStyle "TH Table Text"; $sx.ParagraphFormat.Alignment = 1

    foreach ($i in -20, -21, -22) {   # TOC 1..3
        $ts = $doc.Styles.Item($i); Set-FontProps $ts.Font $FontSize $false
        $ts.ParagraphFormat.SpaceAfter = [single](0); $ts.ParagraphFormat.SpaceBefore = [single](0); $ts.ParagraphFormat.Alignment = 0
    }
    $doc.Styles.Item(-21).ParagraphFormat.LeftIndent = [single]((InPt (0.4)))
    $doc.Styles.Item(-22).ParagraphFormat.LeftIndent = [single]((InPt (0.8)))

    # --- Page setup (applies to section 1; later sections inherit) ---------------
    $ps = $doc.Sections.Item(1).PageSetup
    $ps.PaperSize = 7   # A4
    $ps.TopMargin = [single]((InPt $MarginTopIn)); $ps.BottomMargin = [single]((InPt $MarginBottomIn))
    $ps.LeftMargin = [single]((InPt $MarginLeftIn)); $ps.RightMargin = [single]((InPt $MarginRightIn))
    $ps.HeaderDistance = [single]((InPt $HeaderDistanceIn)); $ps.FooterDistance = [single]((InPt 0.5))

    $sel = $word.Selection

    # NOTE: Word's size/indent/spacing properties are COM Single. PowerShell arithmetic
    # (negation, +, *) yields Double, and the COM binder then throws "Specified cast is
    # not valid" - so every such assignment below is wrapped in [single](...).
    function Reset-Para([string]$style = $null) {
        if ($style) { $sel.Style = $doc.Styles.Item($style) } else { $sel.Style = $doc.Styles.Item(-1) }
        # Reset() drops leftover direct formatting so the style's own bold/size apply.
        $sel.ParagraphFormat.Reset(); $sel.Font.Reset()
    }

    function Add-Runs([string]$text) {
        # **bold** and *italic* markdown -> real Word runs (Latin + Thai props).
        foreach ($part in [regex]::Split($text, '(\*\*.+?\*\*|\*.+?\*)')) {
            if ($part -eq "") { continue }
            if ($part -match '^\*\*(.+)\*\*$') {
                $sel.Font.Bold = 1; $sel.Font.BoldBi = 1; $sel.TypeText($matches[1]); $sel.Font.Bold = 0; $sel.Font.BoldBi = 0
            } elseif ($part -match '^\*(.+)\*$') {
                $sel.Font.Italic = 1; $sel.Font.ItalicBi = 1; $sel.TypeText($matches[1]); $sel.Font.Italic = 0; $sel.Font.ItalicBi = 0
            } else { $sel.TypeText($part) }
        }
    }

    function Add-LabeledCaption([string]$style, [string]$text, [string]$sep = " ") {
        # Bold the "ตารางที่ 4.1" / "ภาพที่ 2.1" / "ภาพภาคผนวก ก1" label, keep title normal.
        Reset-Para $style
        if ($text -match '^(\S+\s*\S+)\s+(.*)$') {
            $sel.Font.Bold = 1; $sel.Font.BoldBi = 1; $sel.TypeText($matches[1])
            $sel.Font.Bold = 0; $sel.Font.BoldBi = 0; $sel.TypeText($sep + $matches[2])
        } else { $sel.TypeText($text) }
        $sel.TypeParagraph()
    }

    function Insert-Field([string]$code) {
        $f = $doc.Fields.Add($sel.Range, -1, $code, $false)
        $sel.EndKey(6) | Out-Null
        $sel.TypeParagraph()
    }

    function Flush-Table($rows, [string]$mode) {
        if ($rows.Count -eq 0) { return }
        $ncol = ($rows | ForEach-Object { $_.Count } | Measure-Object -Maximum).Maximum
        Reset-Para "TH Table Text"
        $start = $sel.Start
        foreach ($r in $rows) {
            $cells = @($r) + @(1..$ncol | ForEach-Object { "" }) | Select-Object -First $ncol
            $sel.TypeText(($cells -join [char]9)); $sel.TypeParagraph()
        }
        $rng = $doc.Range($start, $sel.Start - 1)
        $t = $rng.ConvertToTable(1, $rows.Count, $ncol)   # wdSeparateByTabs
        $t.Range.Style = $doc.Styles.Item("TH Table Text")
        $t.Rows.AllowBreakAcrossPages = 0
        for ($ri = 1; $ri -le $t.Rows.Count; $ri++) { $t.Cell($ri, 1).Range.ParagraphFormat.Alignment = 0 }
        $hdr = $t.Rows.Item(1); $hdr.Range.Font.Bold = 1; $hdr.Range.Font.BoldBi = 1; $hdr.HeadingFormat = -1
        for ($ci = 1; $ci -le $ncol; $ci++) { $t.Cell(1, $ci).Range.ParagraphFormat.Alignment = 1 }
        if ($mode -eq "apa") {
            # Three-line table: top rule, rule under header, bottom rule.
            $t.Borders.Enable = 0
            $t.Borders.Item(-1).LineStyle = 1      # top
            $t.Borders.Item(-3).LineStyle = 1      # bottom
            $hdr.Borders.Item(-3).LineStyle = 1
        } else { $t.Borders.Enable = 1 }

        # Column widths. Word's AutoFit-to-window splits width evenly, which crushes
        # a long text column (e.g. questionnaire items) into a one-word-per-line
        # strip. Instead: short columns get just what their longest cell needs, and
        # "text" columns (longest cell > 24 chars) share the rest in proportion.
        $maxLen = @(0) * $ncol
        foreach ($r in $rows) { for ($c = 0; $c -lt $r.Count -and $c -lt $ncol; $c++) {
            $len = ($r[$c] -replace '\s+', ' ').Trim().Length
            if ($len -gt $maxLen[$c]) { $maxLen[$c] = $len } } }
        $wide = @(0..($ncol - 1) | Where-Object { $maxLen[$_] -gt 24 })
        $pgs = $doc.Sections.Item(1).PageSetup
        $usable = $pgs.PageWidth - $pgs.LeftMargin - $pgs.RightMargin
        if ($wide.Count -eq 0) {
            $t.AutoFitBehavior(1); $t.AutoFitBehavior(2)
        } else {
            $t.AllowAutoFit = $false
            $widths = @(0.0) * $ncol; $narrowSum = 0.0
            for ($c = 0; $c -lt $ncol; $c++) {
                if ($wide -notcontains $c) {
                    $widths[$c] = CmPt ([math]::Min(4.5, [math]::Max(1.0, 0.24 * $maxLen[$c] + 0.6)))
                    $narrowSum += $widths[$c]
                }
            }
            # Many numeric columns (e.g. an ANOVA table) can leave no room for the text
            # column: keep at least 35% of the line for text and shrink the rest to fit.
            $minWide = 0.35 * $usable
            if ($usable - $narrowSum -lt $minWide) {
                $scale = ($usable - $minWide) / $narrowSum
                for ($c = 0; $c -lt $ncol; $c++) { if ($wide -notcontains $c) { $widths[$c] = $widths[$c] * $scale } }
                $narrowSum = $usable - $minWide
            }
            $wideTotal = ($wide | ForEach-Object { $maxLen[$_] } | Measure-Object -Sum).Sum
            foreach ($c in $wide) { $widths[$c] = ($usable - $narrowSum) * $maxLen[$c] / $wideTotal }
            # Set per cell: Columns.Item(n).Width throws "Value out of range" on some tables.
            for ($ri = 1; $ri -le $t.Rows.Count; $ri++) {
                for ($c = 0; $c -lt $ncol; $c++) { $t.Cell($ri, $c + 1).Width = [single]($widths[$c]) }
            }
            # Long text reads better flush left (header row stays centred).
            foreach ($c in $wide) {
                for ($ri = 2; $ri -le $t.Rows.Count; $ri++) { $t.Cell($ri, $c + 1).Range.ParagraphFormat.Alignment = 0 }
            }
        }
        $t.Rows.Alignment = 1
        $sel.EndKey(6) | Out-Null
    }

    $sectionMarks = @{}      # "front"/"body" -> section index
    $inTable = $false; $tableRows = New-Object System.Collections.ArrayList; $tableMode = "grid"

    foreach ($raw in $lines) {
        $line = $raw.TrimEnd()
        if ($inTable) {
            if ($line -match '^\[TR\](.*)$') { [void]$tableRows.Add(@($matches[1] -split '\s*\|\s*')); continue }
            if ($line -match '^\[/TABLE\]') { Flush-Table $tableRows $tableMode; $inTable = $false; $tableRows.Clear(); continue }
            if ($line -eq "") { continue }
            throw "Unexpected line inside [TABLE] block: $line"
        }
        if ($line -eq "" -or $line.StartsWith("#")) { continue }

        if ($line -match '^\[SECTION:(front|body)\]$') {
            $sel.InsertBreak(2)   # wdSectionBreakNextPage
            $sectionMarks[$matches[1]] = $doc.Sections.Count
            continue
        }
        if ($line -eq '[PAGEBREAK]') { $sel.InsertBreak(7); continue }
        if ($line -match '^\[BLANK(?::(\d+))?\]$') {
            $n = 1; if ($matches[1]) { $n = [int]$matches[1] }
            Reset-Para; for ($k = 0; $k -lt $n; $k++) { $sel.TypeParagraph() }; continue
        }
        if ($line -match '^\[(C|L|R)(?::(\d+))?(?::(b))?\](.*)$') {
            Reset-Para "TH Plain"
            $sel.ParagraphFormat.Alignment = @{C=1; L=0; R=2}[$matches[1]]
            $sz = $FontSize; if ($matches[2]) { $sz = [int]$matches[2] }
            $sel.Font.Size = [single]($sz); $sel.Font.SizeBi = [single]($sz)
            $b = [int]([bool]$matches[3]); $sel.Font.Bold = $b; $sel.Font.BoldBi = $b
            Add-Runs $matches[4]; $sel.TypeParagraph()
            $sel.Font.Size = [single]($FontSize); $sel.Font.SizeBi = [single]($FontSize)
            continue
        }
        if ($line -match '^\[FH\](.*)$') { Reset-Para $StyFront; $sel.TypeText($matches[1]); $sel.TypeParagraph(); continue }
        if ($line -match '^\[(CH|APPX)\](.*)$') {
            # "บทที่ 1|บทนำ" -> two centred lines in one Heading 1 paragraph (manual line
            # break), so the TOC entry reads "บทที่ 1 บทนำ" as one line.
            $parts = $matches[2] -split '\|', 2
            Reset-Para; $sel.Style = $doc.Styles.Item(-2)
            $sel.TypeText($parts[0].Trim())
            if ($parts.Count -gt 1) { $sel.TypeText([string][char]11 + $parts[1].Trim()) }
            $sel.TypeParagraph(); continue
        }
        if ($line -match '^\[BACK\](.*)$') { Reset-Para; $sel.Style = $doc.Styles.Item(-2); $sel.TypeText($matches[1]); $sel.TypeParagraph(); continue }
        if ($line -match '^\[H2\](.*)$') { Reset-Para; $sel.Style = $doc.Styles.Item(-3); $sel.TypeText($matches[1]); $sel.TypeParagraph(); continue }
        if ($line -match '^\[H3\](.*)$') { Reset-Para; $sel.Style = $doc.Styles.Item(-4); $sel.TypeText($matches[1]); $sel.TypeParagraph(); continue }
        if ($line -match '^\[P\](.*)$') {
            Reset-Para "TH Body"
            Add-Runs $matches[1]; $sel.TypeParagraph(); continue
        }
        if ($line -match '^\[PN\](.*)$') {
            Reset-Para "TH Body NoIndent"
            Add-Runs $matches[1]; $sel.TypeParagraph(); continue
        }
        if ($line -match '^\[LI(2|3)?\](.*)$') {
            $lvl = 1; if ($matches[1]) { $lvl = [int]$matches[1] }
            Reset-Para "TH List $lvl"
            Add-Runs $matches[2]; $sel.TypeParagraph(); continue
        }
        if ($line -match '^\[KW\]([^:：]+[:：])(.*)$') {
            Reset-Para "TH Keywords"
            $sel.Font.Bold = 1; $sel.Font.BoldBi = 1; $sel.TypeText($matches[1]); $sel.Font.Bold = 0; $sel.Font.BoldBi = 0
            Add-Runs $matches[2]; $sel.TypeParagraph(); continue
        }
        if ($line -match '^\[TCAP\](.*)$') { Add-LabeledCaption $StyTCap $matches[1] ([string][char]9); continue }
        if ($line -match '^\[FCAP\](.*)$') { Add-LabeledCaption $StyFCap $matches[1]; continue }
        if ($line -match '^\[TABLE(?::(apa|grid))?\]$') {
            $inTable = $true; $tableMode = "grid"; if ($matches[1]) { $tableMode = $matches[1] }; continue
        }
        if ($line -match '^\[NOTE\](.*)$') {
            Reset-Para "TH Note"
            if ($matches[1] -match '^([^:：]+[:：])(.*)$') {
                $sel.Font.Bold = 1; $sel.Font.BoldBi = 1; $sel.TypeText($matches[1]); $sel.Font.Bold = 0; $sel.Font.BoldBi = 0
                Add-Runs $matches[2]
            } else { Add-Runs $matches[1] }
            $sel.TypeParagraph(); continue
        }
        if ($line -match '^\[IMG\]([^|]+)(?:\|([\d.]+))?$') {
            $p = $matches[1].Trim(); if (-not [System.IO.Path]::IsPathRooted($p)) { $p = Join-Path $baseDir $p }
            if (-not (Test-Path $p)) { throw "Image not found: $p" }
            Reset-Para "TH Figure"
            $shape = $sel.InlineShapes.AddPicture($p)
            $wcm = 14.0; if ($matches[2]) { $wcm = [double]$matches[2] }
            $shape.LockAspectRatio = -1; $shape.Width = [single]((CmPt $wcm))
            $sel.TypeParagraph(); continue
        }
        if ($line -eq '[TOC]') { Reset-Para "TH Plain"; Insert-Field ('TOC \o "1-' + $TocLevels + '" \h \z \t "' + $StyFront + ',1"'); continue }
        if ($line -eq '[LOT]') { Reset-Para "TH Plain"; Insert-Field ('TOC \h \z \t "' + $StyTCap + ',1"'); continue }
        if ($line -eq '[LOF]') { Reset-Para "TH Plain"; Insert-Field ('TOC \h \z \t "' + $StyFCap + ',1"'); continue }
        if ($line -match '^\[REF\](.*)$') {
            Reset-Para "TH Reference"
            Add-Runs $matches[1]; $sel.TypeParagraph(); continue
        }
        throw "Unknown tag on line: $line"
    }
    if ($inTable) { throw "[TABLE] block not closed with [/TABLE]" }

    # --- Page numbers per section ------------------------------------------------
    # section 1 (cover) = none; front = Thai letters ก ข ค; body = 1 2 3.
    $align = @{right=2; center=1}[$PageNumAlign]
    for ($s = 1; $s -le $doc.Sections.Count; $s++) {
        $sec = $doc.Sections.Item($s)
        $hf = if ($PageNumPlace -eq "header") { $sec.Headers.Item(1) } else { $sec.Footers.Item(1) }
        if ($s -gt 1) { $hf.LinkToPrevious = $false }
    }
    for ($s = 1; $s -le $doc.Sections.Count; $s++) {
        $sec = $doc.Sections.Item($s)
        $hf = if ($PageNumPlace -eq "header") { $sec.Headers.Item(1) } else { $sec.Footers.Item(1) }
        $hf.Range.Text = ""
        $isFront = ($sectionMarks.ContainsKey("front") -and $s -ge $sectionMarks["front"] -and (-not $sectionMarks.ContainsKey("body") -or $s -lt $sectionMarks["body"]))
        $isBody  = ($sectionMarks.ContainsKey("body") -and $s -ge $sectionMarks["body"])
        $isCover = ($s -eq 1 -and $sectionMarks.Count -gt 0)
        if ($isCover) { continue }
        $pn = $hf.PageNumbers
        if ($isFront) { $pn.NumberStyle = 53 }   # wdPageNumberStyleThaiLetter
        else { $pn.NumberStyle = 0 }
        if ($s -eq $sectionMarks["front"] -or $s -eq $sectionMarks["body"]) { $pn.RestartNumberingAtSection = $true; $pn.StartingNumber = 1 }
        $r = $hf.Range
        $doc.Fields.Add($r, 33) | Out-Null        # wdFieldPage
        $hf.Range.ParagraphFormat.Alignment = $align
        Set-FontProps $hf.Range.Font $FontSize $false
    }

    # --- Update TOC / LOT / LOF twice (their own length shifts page numbers) -----
    for ($k = 0; $k -lt 2; $k++) {
        $doc.Repaginate()
        foreach ($toc in $doc.TablesOfContents) { $toc.Update() }
    }
    # TOC fields carry their own char formatting; normalise to the report font.
    foreach ($toc in $doc.TablesOfContents) { Set-FontProps $toc.Range.Font $FontSize $false }

    $doc.SaveAs([ref]$OutputPath, [ref]16)
    if ($PdfPath) { $doc.SaveAs([ref]([System.IO.Path]::GetFullPath($PdfPath)), [ref]17) }
    $pages = $doc.ComputeStatistics(2)
    Write-Output "PAGES=$pages"
    Write-Output "SAVED=$OutputPath"
}
finally {
    if ($doc) { $doc.Close([ref]0) }
    if ($word) { $word.Quit(); [System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null }
    [GC]::Collect(); [GC]::WaitForPendingFinalizers()
}
