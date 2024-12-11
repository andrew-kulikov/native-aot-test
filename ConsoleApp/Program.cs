using System.Collections.Concurrent;

var t = new Thread(RunLoad);
t.Start();
Console.ReadLine();
void RunLoad()
{
    var queue = new ConcurrentQueue<object>();
    while (true)
    {
        var obj = new
        {
            Property1 = "Value1",
            Property2 = "Value2",
            Property3 = "Value3",
            Property4 = "Value4",
            Property5 = "Value5",
            Property6 = "Value6",
            Property7 = "Value7",
            Property8 = "Value8",
            Property9 = "Value9",
            Property10 = "Value10",
            Property11 = "Value11",
            Property12 = "Value12",
            Property13 = "Value13",
            Property14 = "Value14",
            Property15 = "Value15",
            Property16 = "Value16",
            Property17 = "Value17",
            Property18 = "Value18",
            Property19 = "Value19",
            Property20 = "Value20",
            Property21 = "Value21",
            Property22 = "Value22",
            Property23 = "Value23",
            Property24 = "Value24",
            Property25 = "Value25",
            Property26 = "Value26",
            Property27 = "Value27",
            Property28 = "Value28",
            Property29 = "Value29",
            Property30 = "Value30",
            Property31 = "Value31",
            Property32 = "Value32",
            Property33 = "Value33",
            Property34 = "Value34",
            Property35 = "Value35",
            Property36 = "Value36",
            Property37 = "Value37",
            Property38 = "Value38",
            Property39 = "Value39",
            Property40 = "Value40",
            Property41 = "Value41",
            Property42 = "Value42",
            Property43 = "Value43",
            Property44 = "Value44",
            Property45 = "Value45",
            Property46 = "Value46",
            Property47 = "Value47",
            Property48 = "Value48",
            Property49 = "Value49",
            Property50 = "Value50",
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