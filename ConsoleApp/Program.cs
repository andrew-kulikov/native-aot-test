using System.Diagnostics;

var sample = args.ElementAtOrDefault(0);
if (sample == null)
{
    Console.WriteLine("Please select a sample:");
    Console.WriteLine("1: AutofacFuncSample");
    Console.WriteLine("2: NewtonsoftReadonlyListSample");
    Console.WriteLine("3: NewtonsoftGenericSample");
    Console.WriteLine("4: AsyncSample");
    return;
}

var stopwatch = Stopwatch.StartNew();
switch (sample)
{
    case "1":
        Console.WriteLine("Running AutofacFuncSample");
        AutofacFuncSample.Run();
        break;
    case "2":
        Console.WriteLine("Running NewtonsoftReadonlyListSample");
        NewtonsoftReadonlyListSample.Run();
        break;
    case "3":
        Console.WriteLine("Running NewtonsoftGenericSample");
        NewtonsoftGenericSample.Run();
        break;
    case "4":
        Console.WriteLine("Running AsyncSample");
        AsyncSample.Run().GetAwaiter().GetResult();
        break;
}
stopwatch.Stop();
using var process = Process.GetCurrentProcess();
Console.WriteLine($"Time taken: {stopwatch.Elapsed}");
Console.WriteLine($"Peak working set: {process.PeakWorkingSet64} bytes");
Console.WriteLine($"Private memory: {process.PrivateMemorySize64} bytes");
Console.WriteLine($"Managed heap: {GC.GetTotalMemory(forceFullCollection: false)} bytes");