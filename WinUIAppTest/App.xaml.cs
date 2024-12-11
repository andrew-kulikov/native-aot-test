using System;
using System.Collections.Concurrent;
using System.Threading;
using Microsoft.UI.Xaml;

namespace WinUIAppTest;

public partial class App : Application
{
    private Window? m_window;

    public App()
    {
        InitializeComponent();

        var t = new Thread(RunLoad);
        t.Start();
    }

    protected override void OnLaunched(LaunchActivatedEventArgs args)
    {
        m_window = new MainWindow();
        m_window.Activate();
    }

    public static void RunLoad()
    {
        var queue = new ConcurrentQueue<object>();
        while (true)
        {
            var obj = new
            {
                Property1 = new int[1000]
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
