using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using RudderStack.Model;

namespace RudderStack
{
    /// <summary>
    /// Config required to initialize the client
    /// </summary>
    public class RudderConfig
    {
        /// <summary>
        /// The REST API endpoint
        /// </summary>
        internal string Host { get; set; }

        internal string UserAgent { get; set; }

        internal string Proxy { get; set; }

        internal int MaxQueueSize { get; set; }

        internal int FlushAt { get; set; }

        internal bool Async { get; set; }

        internal TimeSpan Timeout { get; set; }

        internal int FlushIntervalInMillis { get; private set; }

        public bool Send { get; set; }

        internal int Threads { get; set; }

        /// <summary>
        ///
        /// </summary>
        /// <param name="host">Endpoint for tracking api for Proxy Service</param>
        /// <param name="proxy"></param>
        /// <param name="timeout"></param>
        /// <param name="maxQueueSize">Queue size</param>
        /// <param name="flushAt">Number of items in a batch to upload</param>
        /// <param name="async">Sets whether the flushing to the server is synchronous or asynchronous</param>
        /// <param name="threads">Count of concurrent internal threads to post data from queue</param>
        /// <param name="flushInterval">The frequency, in seconds, to send data to RudderStack</param>
        /// <param name="send">Don’t send data to RudderStack</param>
        /// <param name="userAgent">Sets User Agent Header</param>
        public RudderConfig(
            string host = "https://hosted.rudderlabs.com",
            string proxy = null,
            TimeSpan? timeout = null,
            int maxQueueSize = 10000,
            int flushAt = 20,
            bool async = true,
            int threads = 1,
            double flushInterval = 10,
            bool send = false,
            string userAgent = null
            )
        {
            this.Host = host;
            this.Proxy = proxy ?? "";
            this.Timeout = timeout ?? TimeSpan.FromSeconds(5);
            this.MaxQueueSize = maxQueueSize;
            this.FlushAt = flushAt;
            this.Async = async;
            this.FlushIntervalInMillis = (int)(flushInterval * 1000);
            this.Send = send;
            this.UserAgent = userAgent ?? GetDefaultUserAgent();
            this.Threads = threads;
        }

        private static string GetDefaultUserAgent()
        {
            var lib = new RudderContext()["library"] as Dict;
            return $"{lib["name"]}/{lib["version"]}";
        }


        /// <summary>
        /// Set the API host server address, instead of default server "https://hosted.rudderlabs.com"
        /// </summary>
        /// <param name="host">Host server url</param>
        /// <returns></returns>
        public RudderConfig SetHost(string host)
        {
            this.Host = host;
            return this;
        }

        /// <summary>
        /// Set the proxy server Uri
        /// </summary>
        /// <param name="proxy">Proxy server Uri</param>
        /// <returns></returns>
        public RudderConfig SetProxy(string proxy)
        {
            this.Proxy = proxy;
            return this;
        }

        /// <summary>
        /// Sets the maximum amount of timeout on the HTTP request flushes to the server.
        /// </summary>
        /// <param name="timeout"></param>
        /// <returns></returns>
        public RudderConfig SetTimeout(TimeSpan timeout)
        {
            this.Timeout = timeout;
            return this;
        }

        /// <summary>
        /// Sets the maximum amount of items that can be in the queue before no more are accepted.
        /// </summary>
        /// <param name="maxQueueSize"></param>
        /// <returns></returns>
        public RudderConfig SetMaxQueueSize(int maxQueueSize)
        {
            this.MaxQueueSize = maxQueueSize;
            return this;
        }

        /// <summary>
        /// Sets the maximum amount of messages to send per batch
        /// </summary>
        /// <param name="maxBatchSize"></param>
        /// <returns></returns>
        [Obsolete("Use the new method SetFlushAt")]
        public RudderConfig SetMaxBatchSize(int maxBatchSize)
        {
            return SetFlushAt(maxBatchSize);
        }

        /// <summary>
        /// Sets the maximum amount of messages to send per batch
        /// </summary>
        /// <param name="flushAt"></param>
        /// <returns></returns>
        public RudderConfig SetFlushAt(int flushAt)
        {
            this.FlushAt = flushAt;
            return this;
        }

        /// <summary>
        /// Count of concurrent internal threads to post data from queue
        /// </summary>
        /// <param name="threads"></param>
        /// <returns></returns>
        public RudderConfig SetThreads(int threads)
        {
            Threads = threads;
            return this;
        }

        /// <summary>
        /// Sets whether the flushing to the server is synchronous or asynchronous.
        ///
        /// True is the default and will allow your calls to Analytics.Client.Identify(...), Track(...), etc
        /// to return immediately and to be queued to be flushed on a different thread.
        ///
        /// False is convenient for testing but should not be used in production. False will cause the
        /// HTTP requests to happen immediately.
        ///
        /// </summary>
        /// <param name="async">True for async flushing, false for blocking flushing</param>
        /// <returns></returns>
        public RudderConfig SetAsync(bool async)
        {
            this.Async = async;
            return this;
        }

        public RudderConfig SetUserAgent(string userAgent)
        {
            this.UserAgent = userAgent;
            return this;
        }

        /// <summary>
        /// Don’t send data to RudderStack
        /// </summary>
        /// <param name="send"></param>
        /// <returns></returns>
        public RudderConfig SetSend(bool send)
        {
            this.Send = send;
            return this;
        }

        /// <summary>
        /// Set the interval in seconds at which the client should flush events.
        /// </summary>
        /// <param name="interval"></param>
        /// <returns></returns>
        public RudderConfig SetFlushInterval(double interval)
        {
            this.FlushIntervalInMillis = (int)(interval * 1000);
            return this;
        }
    }
}