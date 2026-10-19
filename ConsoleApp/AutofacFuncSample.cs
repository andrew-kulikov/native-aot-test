using Ioc;
using Ioc.Autofac;

public class AutofacFuncSample
{
    public static void Run()
    {
        var cb = new AutofacContainerBuilder();
        cb.Register<MyService>();

        var container = cb.Build();
        var factory = container.Resolve<Func<MyService2, MyService>>();
        var myService = factory(new MyService2());
        myService.DoSomething();
    }
}

public class MyService
{
    private readonly MyService2 _myService2;

    public MyService(MyService2 myService2)
    {
        _myService2 = myService2;
    }

    public void DoSomething()
    {
        Console.WriteLine("Doing something 1");
        _myService2.DoSomething();
    }
}

public class MyService2
{
    public void DoSomething()
    {
        Console.WriteLine("Doing something 2");
    }
}
