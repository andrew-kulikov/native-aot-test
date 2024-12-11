using System;
using System.Collections.Concurrent;
using System.Threading;
using Windows.UI.Xaml;

namespace UwpDotnet;
#if DISABLE_XAML_GENERATED_MAIN
public static class Program
{
    [MTAThread]
    public static void Main(string[] args)
    {
        var t = new Thread(RunLoad);
        t.Start();
        Application.Start(par => new App());
    }

    public static void RunLoad()
    {
        var queue = new ConcurrentQueue<object>();
        while (true)
        {
            var obj = new
            {
                Property51 = new int[1000]
            };
            if (queue.Count > 100000)
            {
                queue.TryDequeue(out _);
            }
            queue.Enqueue(obj);
            if (Random.Shared.Next() % 1000 == 0)
            {
                Thread.Sleep(10);
            }
        }
    }
}
#endif
