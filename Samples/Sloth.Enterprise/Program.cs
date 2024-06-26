using System;
using RudderStack;
using RudderStack.Utils;
using Sloth.Common;

namespace Sloth.Enterprise
{
    class Program
    {

        private const int UserJourneys = 5000;

        static void Main(string[] args)
        {
            var parentPath = Utilities.getParentPath(5, System.IO.Directory.GetCurrentDirectory());
            var filePath = parentPath + "\\.env";
            DotEnv.Load(filePath);
            var writeKey = Environment.GetEnvironmentVariable("WRITE_KEY");

            if (string.IsNullOrWhiteSpace(writeKey)) throw new ArgumentException(nameof(writeKey));

            OnExecute(writeKey);
        }

        private static void OnExecute(string writeKey)
        {
            var config = new RudderConfig()
                .SetMaxQueueSize(100000)
                .SetHost("https://hosted.rudderlabs.com")
                .SetMaxBatchSize(40);
            //.SetRequestCompression(true);

            RudderAnalytics.Initialize(writeKey, config);

            Logger.Handlers += Utils.LoggerOnHandlers;

            for (var i = 0; i < UserJourneys; i++)
            {
                Utils.DoJourney();
            }

            // sending all pendant messages
            RudderAnalytics.Client.Flush();

            Utils.PrintSummary();

            RudderAnalytics.Client.Dispose();
        }
    }
}
