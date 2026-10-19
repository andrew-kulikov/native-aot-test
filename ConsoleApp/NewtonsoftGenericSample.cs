using Newtonsoft.Json;

public class NewtonsoftGenericSample
{
    public static void Run()
    {
        Console.WriteLine("NewtonsoftGenericSample");
        var json = """{ "Items": [{"Name": "Item 1"}]}""";
        var myDto = JsonConvert.DeserializeObject<MyGenericDto<MyDto3>>(json);
        Console.WriteLine($"Ref type items count: {myDto.Items.Count}");
        foreach (var item in myDto.Items)
        {
            Console.WriteLine($"Ref type item name: {item.Name}");
        }

        var json2 = """{ "Items": [1, 2, 3]}""";
        var myDto2 = JsonConvert.DeserializeObject<MyGenericDto<int>>(json2);
        Console.WriteLine($"Value type items count: {myDto2.Items.Count}");
        foreach (var item in myDto2.Items)
        {
            Console.WriteLine($"Value type item: {item}");
        }
    }
}

public class MyGenericDto<T>
{
    public IReadOnlyList<T> Items { get; set; }
}

public class MyDto3
{
    public string Name { get; set; }
}
