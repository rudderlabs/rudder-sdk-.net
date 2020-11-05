using System;
using System.Collections.Generic;

namespace RudderStack.Test
{
    class Program
    {
        static void Main(string[] args)
        {
            Logger.Handlers += Logger_Handlers;

            Analytics.Initialize(RudderStack.Test.Constants.WRITE_KEY);

            Analytics.Client.Track("prateek", "Item Purchased (with .Net 3.5)");
            Analytics.Client.Flush();
        }

        private static void Logger_Handlers(Logger.Level level, string message, IDictionary<string, object> args)
        {
            Console.WriteLine(message);
        }
    }
}
