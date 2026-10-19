using Newtonsoft.Json;

public class NewtonsoftReadonlyListSample
{
    public static void Run()
    {
        var json = """{ "Items": [{"Name": "Item 1"}]}""";
        var myDto = JsonConvert.DeserializeObject<MyDto>(json);
        Console.WriteLine($"Items count: {myDto.Items.Count}");
        foreach (var item in myDto.Items)
        {
            Console.WriteLine($"Item name: {item.Name}");    
        }
    }
}


public class MyDto
{
    public IReadOnlyList<MyDto2> Items { get; set; }
}

public class MyDto2
{
    public string Name { get; set; }
}
