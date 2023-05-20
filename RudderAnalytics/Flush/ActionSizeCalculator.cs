using Newtonsoft.Json;
using RudderStack.Model;

namespace RudderStack.Flush
{
    public class ActionSizeCalculator
    {
        public static int Calculate(BaseAction action)
        {
            return JsonConvert.SerializeObject(action).Length;
        }
    }
}
