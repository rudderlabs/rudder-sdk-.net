using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using Moq;
using NUnit.Framework;
using RudderStack.Model;
using RudderStack.Request;

namespace RudderStack.Test
{
    [TestFixture()]
    public class FlushTests
    {
        private Mock<IRequestHandler> _mockRequestHandler;

        [SetUp]
        public void Init()
        {
            _mockRequestHandler = new Mock<IRequestHandler>();
            _mockRequestHandler
                .Setup(x => x.MakeRequest(It.IsAny<Batch>()))
                .Returns((Batch b) =>
                {
                    b.batch.ForEach(_ => RudderAnalytics.Client.Statistics.IncrementSucceeded());
                    return Task.CompletedTask;
                });

            RudderAnalytics.Dispose();
            Logger.Handlers += LoggingHandler;
        }

        [TearDown]
        public void CleanUp()
        {
            Logger.Handlers -= LoggingHandler;
        }

        [Test()]
        public void SynchronousFlushTest()
        {
            var client = new RudderClient(Constants.WRITE_KEY, new RudderConfig().SetAsync(false), _mockRequestHandler.Object);
            RudderAnalytics.Initialize(client);
            RudderAnalytics.Client.Succeeded += Client_Succeeded;
            RudderAnalytics.Client.Failed += Client_Failed;

            int trials = 10;

            RunTests(RudderAnalytics.Client, trials);

            RudderAnalytics.Client.Flush();

            Assert.AreEqual(trials, RudderAnalytics.Client.Statistics.Submitted);
            Assert.AreEqual(trials, RudderAnalytics.Client.Statistics.Succeeded);
            Assert.AreEqual(0, RudderAnalytics.Client.Statistics.Failed);
        }

        [Test()]
        public void AsynchronousFlushTest()
        {
            var client = new RudderClient(Constants.WRITE_KEY, new RudderConfig().SetAsync(true), _mockRequestHandler.Object);
            RudderAnalytics.Initialize(client);

            RudderAnalytics.Client.Succeeded += Client_Succeeded;
            RudderAnalytics.Client.Failed += Client_Failed;

            int trials = 10;

            RunTests(RudderAnalytics.Client, trials);

            RudderAnalytics.Client.Flush();

            Assert.AreEqual(trials, RudderAnalytics.Client.Statistics.Submitted);
            Assert.AreEqual(trials, RudderAnalytics.Client.Statistics.Succeeded);
            Assert.AreEqual(0, RudderAnalytics.Client.Statistics.Failed);
        }

        [Test]
        public void AsynchronousFlushReportsAnOversizedAction()
        {
            using (var client = new RudderClient("test-key", new RudderConfig().SetSend(false)))
            {
                var failures = new List<BaseAction>();
                var errors = new List<System.Exception>();
                client.Failed += (action, error) =>
                {
                    failures.Add(action);
                    errors.Add(error);
                };

                client.Track("test-user", "oversized", new Dict { { "value", new string('x', 32 * 1024) } });
                client.Track("test-user", "valid");
                client.Flush();

                Assert.AreEqual(2, client.Statistics.Submitted);
                Assert.AreEqual(1, client.Statistics.Failed);
                Assert.AreEqual(1, client.Statistics.Succeeded);
                Assert.That(failures, Has.Count.EqualTo(1));
                Assert.That(((Track)failures[0]).EventName, Is.EqualTo("oversized"));
                Assert.That(errors[0], Is.TypeOf<ArgumentException>());
            }
        }

        [Test()]
        public async Task PerformanceTest()
        {
            var client = new RudderClient(Constants.WRITE_KEY, new RudderConfig(), _mockRequestHandler.Object);
            RudderAnalytics.Initialize(client);

            RudderAnalytics.Client.Succeeded += Client_Succeeded;
            RudderAnalytics.Client.Failed += Client_Failed;

            int trials = 100;

            DateTime start = DateTime.Now;

            Console.WriteLine("starting to trigger events");
            RunTests(RudderAnalytics.Client, trials);
            Console.WriteLine("finnishing to trigger events");

            RudderAnalytics.Client.Flush();

            TimeSpan duration = DateTime.Now.Subtract(start);

            Assert.AreEqual(trials, RudderAnalytics.Client.Statistics.Submitted);
            Assert.AreEqual(trials, RudderAnalytics.Client.Statistics.Succeeded);
            Assert.AreEqual(0, RudderAnalytics.Client.Statistics.Failed);

            Assert.IsTrue(duration.CompareTo(TimeSpan.FromSeconds(20)) < 0);
        }

        private void RunTests(RudderClient client, int trials)
        {
            for (int i = 0; i < trials; i += 1)
            {
                Actions.Random(client);
                if (i % 100 == 0) Thread.Sleep(500);
            }
        }

        void Client_Failed(BaseAction action, System.Exception e)
        {
            Console.WriteLine(String.Format("Action [{0}] {1} failed : {2}",
                action.MessageId, action.Type, e.Message));
        }

        void Client_Succeeded(BaseAction action)
        {
            Console.WriteLine(String.Format("Action [{0}] {1} succeeded.",
                action.MessageId, action.Type));
        }

        static void LoggingHandler(Logger.Level level, string message, IDictionary<string, object> args)
        {
            if (args != null)
            {
                foreach (string key in args.Keys)
                {
                    message += String.Format(" {0}: {1},", "" + key, "" + args[key]);
                }
            }
            Console.WriteLine(String.Format("[FlushTests] [{0}] {1}", level, message));
        }
    }
}

