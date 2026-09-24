// cwxml2bin: convert CodeWalker XML files (*.ydr.xml, *.ytd.xml, *.ycd.xml, ...)
// to binary GTA V resources, and optionally back to XML for verification.
//   cwxml2bin <file.ext.xml> [outdir]        XML -> binary (textures are read
//                                             from the XML file's folder)
//   cwxml2bin --toxml <file.ext> [outdir]     binary -> XML (round-trip check)
using System;
using System.IO;
using System.Xml;
using CodeWalker.GameFiles;

static class Program
{
    static int Main(string[] args)
    {
        if (args.Length < 1)
        {
            Console.Error.WriteLine("usage: cwxml2bin <file.ext.xml> [outdir] | --toxml <file.ext> [outdir]");
            return 2;
        }
        try
        {
            if (args[0] == "--toxml") return ToXml(args[1], args.Length > 2 ? args[2] : null);
            return ToBinary(args[0], args.Length > 1 ? args[1] : null);
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine("ERROR: " + ex);
            return 1;
        }
    }

    static int ToBinary(string input, string outDir)
    {
        var fname = Path.GetFileName(input);
        var mformat = XmlMeta.GetXMLFormat(fname.ToLowerInvariant(), out int trim);
        var doc = new XmlDocument();
        doc.LoadXml(File.ReadAllText(input));
        var folder = Path.GetDirectoryName(Path.GetFullPath(input));
        // textures (*.dds) are expected in a folder named like the file,
        // e.g. w_pi_glock17.ydr.xml -> w_pi_glock17/  (CodeWalker convention)
        var baseName = fname.Substring(0, fname.Length - trim);
        var texFolder = Path.Combine(folder, Path.GetFileNameWithoutExtension(baseName));
        byte[] data = XmlMeta.GetData(doc, mformat, texFolder);
        if (data == null) { Console.Error.WriteLine("conversion returned no data: " + input); return 1; }
        outDir = outDir ?? folder;
        Directory.CreateDirectory(outDir);
        var outPath = Path.Combine(outDir, fname.Substring(0, fname.Length - trim));
        File.WriteAllBytes(outPath, data);
        Console.WriteLine($"{input} -> {outPath} ({data.Length} bytes)");
        return 0;
    }

    static int ToXml(string input, string outDir)
    {
        var data = File.ReadAllBytes(input);
        var fname = Path.GetFileName(input);
        var ext = Path.GetExtension(fname).ToLowerInvariant();
        outDir = outDir ?? Path.GetDirectoryName(Path.GetFullPath(input));
        Directory.CreateDirectory(outDir);
        string xml;
        switch (ext)
        {
            case ".ydr": xml = YdrXml.GetXml(RpfFile.GetResourceFile<YdrFile>(data), outDir); break;
            case ".ytd": xml = YtdXml.GetXml(RpfFile.GetResourceFile<YtdFile>(data), outDir); break;
            case ".ycd": xml = YcdXml.GetXml(RpfFile.GetResourceFile<YcdFile>(data)); break;
            default: Console.Error.WriteLine("unsupported: " + ext); return 1;
        }
        var outPath = Path.Combine(outDir, fname + ".xml");
        File.WriteAllText(outPath, xml);
        Console.WriteLine($"{input} -> {outPath}");
        return 0;
    }
}
