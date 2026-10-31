import json, random
from pathlib import Path

Q = [
{"d":"IAM & Security","m":False,"q":"A developer needs an EC2 instance to read objects from an S3 bucket. What is the most secure way to grant this access?",
 "o":[
  {"t":"Attach an IAM role with the required S3 permissions to the EC2 instance.","c":True,"w":"Instance roles provide temporary credentials delivered via the instance metadata service, with no long-lived secrets to manage or leak."},
  {"t":"Create an IAM user, generate access keys, and store them in the application's config file.","c":False,"w":"Long-lived access keys stored on disk are a common source of credential leaks and are harder to rotate than a role."},
  {"t":"Make the S3 bucket public so the instance can read it over HTTPS.","c":False,"w":"This exposes the data to the entire internet, far beyond what the instance needs."},
  {"t":"Embed the AWS root account credentials in the application.","c":False,"w":"The root account should never be used for day-to-day access and has unrestricted power over the whole account."}
 ]},
{"d":"IAM & Security","m":False,"q":"By default, when a request is evaluated against multiple IAM policies, what happens if one policy has an explicit Deny and another has an explicit Allow for the same action?",
 "o":[
  {"t":"The explicit Deny wins and the request is denied.","c":True,"w":"IAM evaluation logic gives explicit Deny statements priority over any Allow, regardless of how many policies grant access."},
  {"t":"The explicit Allow wins because it was granted by an administrator.","c":False,"w":"Allow never overrides an explicit Deny in the same evaluation."},
  {"t":"The most recently attached policy wins.","c":False,"w":"IAM does not use a 'last writer wins' model; it aggregates all applicable statements."},
  {"t":"The request succeeds only for actions listed in both policies.","c":False,"w":"This describes an intersection model, which is not how IAM evaluates combined policies."}
 ]},
{"d":"IAM & Security","m":False,"q":"A mobile app needs temporary, limited-privilege AWS credentials for users who sign in with a third-party identity provider like Google. Which service issues these credentials?",
 "o":[
  {"t":"AWS STS via Amazon Cognito Identity Pools.","c":True,"w":"Cognito Identity Pools federate external identities and use STS to vend temporary, scoped credentials directly to the app."},
  {"t":"IAM Access Analyzer.","c":False,"w":"Access Analyzer finds unintended resource access; it does not issue credentials."},
  {"t":"AWS Organizations.","c":False,"w":"Organizations manages multi-account structure and policies, not end-user credential issuance."},
  {"t":"AWS Directory Service.","c":False,"w":"Directory Service provides managed Microsoft AD, which is unrelated to federating mobile app users."}
 ]},
{"d":"IAM & Security","m":False,"q":"Which statement correctly distinguishes Security Groups from Network ACLs in a VPC?",
 "o":[
  {"t":"Security groups are stateful and operate at the instance level; NACLs are stateless and operate at the subnet level.","c":True,"w":"This is the core distinction: SG return traffic is automatically allowed, while NACLs require explicit rules for both directions and apply to everything entering or leaving a subnet."},
  {"t":"Security groups only support deny rules, while NACLs only support allow rules.","c":False,"w":"Security groups support only allow rules; NACLs support both allow and deny rules — the reverse of this statement."},
  {"t":"NACLs are stateful and security groups are stateless.","c":False,"w":"This reverses the actual behavior described above."},
  {"t":"Security groups apply to subnets, and NACLs apply to individual instances.","c":False,"w":"This also reverses the actual scopes of each control."}
 ]},
{"d":"Compute (EC2)","m":False,"q":"A batch processing workload can tolerate interruptions and needs to run at the lowest possible cost. Which EC2 purchasing option fits best?",
 "o":[
  {"t":"Spot Instances.","c":True,"w":"Spot offers the deepest discount off On-Demand in exchange for the possibility AWS reclaims the capacity with short notice — fine for interruption-tolerant batch jobs."},
  {"t":"On-Demand Instances.","c":False,"w":"On-Demand is flexible but the most expensive option, with no discount for interruption tolerance."},
  {"t":"Reserved Instances.","c":False,"w":"Reserved Instances require a 1 or 3 year commitment and suit steady-state workloads, not ad hoc interruptible batch jobs."},
  {"t":"Dedicated Hosts.","c":False,"w":"Dedicated Hosts are for licensing or compliance needs requiring a physical server, and are the most expensive option here."}
 ]},
{"d":"Compute (EC2)","m":False,"q":"An application requires the lowest possible network latency between a small cluster of EC2 instances for a tightly coupled HPC workload. What should you use?",
 "o":[
  {"t":"A cluster placement group.","c":True,"w":"Cluster placement groups pack instances close together in a single AZ for the lowest inter-instance network latency, ideal for tightly coupled HPC or low-latency workloads."},
  {"t":"A spread placement group.","c":False,"w":"Spread placement groups maximize separation across distinct hardware to reduce correlated failure, which increases rather than decreases inter-instance latency."},
  {"t":"An Auto Scaling group across three Availability Zones.","c":False,"w":"Spreading across AZs increases network latency between instances compared to keeping them in one AZ."},
  {"t":"Reserved Instances in different Regions.","c":False,"w":"Purchasing option has nothing to do with network placement, and different Regions would add significant latency."}
 ]},
{"d":"Compute (EC2)","m":False,"q":"An Auto Scaling group is configured with a target tracking policy on average CPU utilization. During a sudden traffic spike, what happens?",
 "o":[
  {"t":"The ASG launches additional instances to bring average CPU utilization back toward the target value.","c":True,"w":"Target tracking continuously adjusts capacity up or down to keep the chosen metric near the target, which is exactly this scenario."},
  {"t":"The ASG terminates instances to reduce load.","c":False,"w":"Terminating instances during a CPU spike would push utilization higher, not lower — the opposite of the intended behavior."},
  {"t":"Nothing happens until the next scheduled scaling action.","c":False,"w":"Target tracking reacts dynamically to the metric; it is not limited to fixed schedules."},
  {"t":"The ASG immediately replaces the launch template with a larger instance type.","c":False,"w":"Scaling policies add or remove instances of the configured type; they do not resize the instance type (that would be a manual launch template change)."}
 ]},
{"d":"Compute (EC2)","m":True,"q":"Which of the following are valid reasons to choose an EC2 Reserved Instance over On-Demand? (Select TWO)",
 "o":[
  {"t":"The workload runs continuously with predictable, steady-state usage.","c":True,"w":"Reserved Instances pay off specifically when usage is steady and predictable enough to justify a 1 or 3 year commitment."},
  {"t":"You want a significant discount in exchange for a capacity commitment over a 1 or 3 year term.","c":True,"w":"This is the core value proposition of Reserved Instances: commit to a term, receive a lower effective hourly rate."},
  {"t":"The workload needs to run for only a few hours total.","c":False,"w":"Very short-lived workloads don't benefit from a 1-3 year commitment; On-Demand or Spot fits better."},
  {"t":"You need AWS to be able to interrupt the instance at any time with two minutes' notice.","c":False,"w":"That behavior describes Spot Instances, not Reserved Instances."}
 ]},
{"d":"Storage (S3)","m":False,"q":"Data is accessed frequently for 30 days, then rarely accessed but must still be retrievable within milliseconds for up to a year, after which it can be deleted. What is the most cost-effective S3 configuration?",
 "o":[
  {"t":"A lifecycle rule transitioning objects from S3 Standard to S3 Standard-IA after 30 days, then expiring them after a year.","c":True,"w":"Standard-IA keeps millisecond retrieval while charging less for storage than Standard, matching the 'rarely accessed but still fast' requirement, and the expiration rule handles cleanup automatically."},
  {"t":"Store everything in S3 Glacier Flexible Retrieval from day one.","c":False,"w":"Glacier retrieval takes minutes to hours, not milliseconds, so it fails the access-latency requirement for the first year."},
  {"t":"Store everything in S3 Intelligent-Tiering with no lifecycle rules at all.","c":False,"w":"Intelligent-Tiering works, but a lifecycle rule to Standard-IA is more directly cost-effective once the access pattern is already known, and expiration still needs to be configured."},
  {"t":"Keep all data in S3 Standard for the full year.","c":False,"w":"This meets the latency requirement but costs more than necessary once access frequency drops after 30 days."}
 ]},
{"d":"Storage (S3)","m":False,"q":"A company wants to protect against accidental deletion of important objects in an S3 bucket while still allowing normal overwrites. What should they enable?",
 "o":[
  {"t":"S3 Versioning.","c":True,"w":"Versioning keeps prior versions of an object instead of deleting them outright, so an 'accidental delete' becomes a recoverable delete marker rather than permanent data loss."},
  {"t":"S3 Transfer Acceleration.","c":False,"w":"Transfer Acceleration speeds up uploads over long distances; it has no relation to protecting against deletion."},
  {"t":"S3 Requester Pays.","c":False,"w":"Requester Pays shifts data transfer and request costs to the requester; it does not protect objects from deletion."},
  {"t":"Cross-Region Replication alone, without Versioning.","c":False,"w":"CRR requires Versioning to be enabled on the source bucket in the first place, so it cannot be used alone, and a delete without a protective mechanism would still replicate as a delete."}
 ]},
{"d":"Storage (S3)","m":False,"q":"Which S3 feature would you use to automatically encrypt all new objects uploaded to a bucket, even if the uploading application does not specify encryption headers?",
 "o":[
  {"t":"Default bucket encryption (SSE-S3 or SSE-KMS).","c":True,"w":"Default encryption applies the configured encryption to every new object automatically, removing the need for the client to set encryption headers itself."},
  {"t":"S3 Object Lock.","c":False,"w":"Object Lock enforces WORM retention policies to prevent deletion or overwrite; it does not perform encryption."},
  {"t":"S3 Select.","c":False,"w":"S3 Select retrieves a subset of data from an object using SQL-like expressions; it is unrelated to encryption."},
  {"t":"Same-Region Replication.","c":False,"w":"Replication copies objects to another bucket; it does not enforce encryption on upload."}
 ]},
{"d":"Storage (S3)","m":False,"q":"An application frequently reads the same small set of S3 objects, and access patterns are unpredictable and change over time. Which storage class minimizes cost with no operational overhead?",
 "o":[
  {"t":"S3 Intelligent-Tiering.","c":True,"w":"Intelligent-Tiering automatically moves objects between access tiers based on actual usage patterns, which is exactly suited to unpredictable, changing access without manual lifecycle rules."},
  {"t":"S3 One Zone-IA.","c":False,"w":"One Zone-IA is cheaper but stores data in a single AZ, risking availability, and is meant for infrequently accessed, non-critical data, not unpredictable frequent-access patterns."},
  {"t":"S3 Glacier Deep Archive.","c":False,"w":"Deep Archive has retrieval times measured in hours and is meant for data accessed once or twice a year, not frequent reads."},
  {"t":"S3 Standard with manual lifecycle rules reviewed monthly.","c":False,"w":"Manual rules add operational overhead and react too slowly to patterns that change unpredictably, unlike Intelligent-Tiering's automatic monitoring."}
 ]},
{"d":"Networking (VPC)","m":False,"q":"A private subnet needs outbound internet access for software updates, but resources in it must not be directly reachable from the internet. What should you deploy?",
 "o":[
  {"t":"A NAT Gateway in a public subnet, with the private subnet's route table pointing default traffic to it.","c":True,"w":"A NAT Gateway allows outbound-initiated connections to the internet while blocking unsolicited inbound connections, which is exactly the private-subnet requirement."},
  {"t":"An Internet Gateway attached directly to the private subnet's route table.","c":False,"w":"An Internet Gateway allows direct bidirectional access, including inbound, which breaks the 'not reachable from the internet' requirement."},
  {"t":"A VPC endpoint for Amazon S3.","c":False,"w":"Gateway/interface VPC endpoints provide private access to specific AWS services, not general internet access for software updates."},
  {"t":"A Direct Connect connection.","c":False,"w":"Direct Connect is a dedicated network link to on-premises infrastructure, not a mechanism for general internet egress."}
 ]},
{"d":"Networking (VPC)","m":False,"q":"A company has 12 VPCs across several AWS accounts that all need to communicate with each other and with an on-premises data center, while keeping routing manageable as they add more VPCs. What should they use?",
 "o":[
  {"t":"AWS Transit Gateway.","c":True,"w":"Transit Gateway acts as a central hub so each VPC and the on-premises network peers with it once, avoiding the unmanageable mesh of individual peering connections as the count of VPCs grows."},
  {"t":"Individual VPC peering connections between every pair of VPCs.","c":False,"w":"Peering is not transitive and scales as a full mesh, which becomes operationally unmanageable well before 12 VPCs with on-premises connectivity too."},
  {"t":"A single NAT Gateway shared across all VPCs.","c":False,"w":"NAT Gateways provide internet egress for a subnet, not inter-VPC or on-premises connectivity."},
  {"t":"Route 53 Resolver rules alone.","c":False,"w":"Resolver rules handle DNS resolution forwarding; they don't establish network-layer connectivity between VPCs."}
 ]},
{"d":"Networking (VPC)","m":False,"q":"You want to route users to the lowest-latency endpoint among healthy resources deployed in multiple AWS Regions. Which Route 53 routing policy fits?",
 "o":[
  {"t":"Latency-based routing.","c":True,"w":"Latency-based routing directs each user to the Region that historically gives them the lowest round-trip latency, among the endpoints you've marked healthy."},
  {"t":"Simple routing.","c":False,"w":"Simple routing returns a single static answer with no health or latency awareness."},
  {"t":"Weighted routing.","c":False,"w":"Weighted routing distributes traffic by assigned proportions, not by measured latency."},
  {"t":"Geolocation routing.","c":False,"w":"Geolocation routes based on the user's geographic location, not measured network latency, which can diverge from the fastest endpoint."}
 ]},
{"d":"Networking (VPC)","m":False,"q":"Two VPCs in different AWS accounts need to communicate privately without traversing the public internet, and neither has overlapping CIDR blocks. What is the simplest solution for a one-off connection between just these two VPCs?",
 "o":[
  {"t":"A VPC peering connection.","c":True,"w":"VPC peering is the simplest point-to-point private connection between two VPCs, including across accounts, as long as CIDR ranges don't overlap."},
  {"t":"AWS Transit Gateway.","c":False,"w":"Transit Gateway is justified when connecting many VPCs/networks; for just two VPCs it adds unnecessary cost and complexity."},
  {"t":"A Site-to-Site VPN.","c":False,"w":"Site-to-Site VPN connects a VPC to an on-premises network over the internet via IPsec tunnels, not two VPCs to each other."},
  {"t":"AWS Direct Connect.","c":False,"w":"Direct Connect links on-premises infrastructure to AWS over a dedicated line; it isn't used to connect two VPCs to each other."}
 ]},
{"d":"Databases","m":False,"q":"A production RDS database needs automatic failover to a standby in another AZ if the primary fails, with no data loss on failover. What should you enable?",
 "o":[
  {"t":"RDS Multi-AZ deployment.","c":True,"w":"Multi-AZ maintains a synchronously replicated standby in another AZ and automatically fails over to it, preserving committed data."},
  {"t":"A read replica in another Region.","c":False,"w":"Read replicas use asynchronous replication and require manual promotion; they're for read scaling and DR, not automatic zero-data-loss failover."},
  {"t":"RDS automated backups only.","c":False,"w":"Backups allow point-in-time restore but don't provide automatic failover during an outage."},
  {"t":"Amazon ElastiCache in front of the database.","c":False,"w":"ElastiCache is a caching layer to reduce database load; it does not provide database failover."}
 ]},
{"d":"Databases","m":False,"q":"An application has a read-heavy workload on a single RDS MySQL database, and query latency is increasing as read traffic grows. What is the most direct way to scale read capacity?",
 "o":[
  {"t":"Create one or more RDS Read Replicas and direct read traffic to them.","c":True,"w":"Read replicas offload read queries from the primary instance using asynchronous replication, directly scaling read capacity."},
  {"t":"Enable Multi-AZ deployment.","c":False,"w":"Multi-AZ provides failover resilience; the standby is not used to serve read traffic in standard Multi-AZ RDS, so it doesn't address read scaling here."},
  {"t":"Switch to a larger EC2 instance type.","c":False,"w":"RDS is a managed service; the question is about database read capacity, not an EC2 instance the application runs on."},
  {"t":"Increase the database's allocated storage.","c":False,"w":"Storage size affects capacity for data, not read query throughput."}
 ]},
{"d":"Databases","m":False,"q":"A workload has highly unpredictable and spiky traffic on a DynamoDB table, and the team doesn't want to manage capacity manually. Which capacity mode should they choose?",
 "o":[
  {"t":"On-Demand capacity mode.","c":True,"w":"On-Demand automatically scales to handle traffic spikes instantly and bills per request, removing the need to provision or manage throughput."},
  {"t":"Provisioned capacity mode with no auto scaling configured.","c":False,"w":"Fixed provisioned capacity without auto scaling would throttle requests during spikes rather than absorb them."},
  {"t":"Reserved capacity on an EC2 instance running a self-managed database.","c":False,"w":"This abandons DynamoDB entirely and reintroduces the operational burden the question says to avoid."},
  {"t":"Provisioned capacity with manual weekly capacity reviews.","c":False,"w":"Weekly manual reviews react far too slowly to traffic that is spiky and unpredictable."}
 ]},
{"d":"Databases","m":False,"q":"Which combination correctly matches a caching engine to its primary strength?",
 "o":[
  {"t":"ElastiCache for Redis supports complex data structures and persistence; ElastiCache for Memcached is simpler and supports easy horizontal scaling via multi-threading.","c":True,"w":"This matches the real distinction: Redis offers richer data types, replication, and persistence, while Memcached favors simplicity and multi-threaded scaling for pure caching."},
  {"t":"Memcached supports built-in replication and persistence, while Redis does not.","c":False,"w":"This reverses the actual capabilities — Redis is the one with replication and persistence support."},
  {"t":"Both engines automatically replicate data across AWS Regions by default.","c":False,"w":"Neither engine does cross-Region replication by default; that requires Global Datastore (Redis-specific) configured explicitly."},
  {"t":"ElastiCache cannot be used alongside RDS in the same application.","c":False,"w":"ElastiCache is commonly used as a caching layer in front of RDS; there's no such restriction."}
 ]},
{"d":"Serverless & Messaging","m":False,"q":"A producer service needs to send messages that must be processed by exactly one consumer each, with consumers polling for work and deleting messages once processed. What should you use?",
 "o":[
  {"t":"Amazon SQS.","c":True,"w":"SQS is a point-to-point queue: each message is delivered to one consumer at a time, and consumers poll and delete messages after processing, matching the described pattern exactly."},
  {"t":"Amazon SNS.","c":False,"w":"SNS is pub/sub: it pushes each message to every subscriber, not to a single consumer picked from a pool."},
  {"t":"AWS Step Functions.","c":False,"w":"Step Functions orchestrates multi-step workflows; it is not a message queue for distributing work among consumers."},
  {"t":"Amazon EventBridge.","c":False,"w":"EventBridge routes events to multiple targets based on rules; it is not designed as a single-consumer work queue."}
 ]},
{"d":"Serverless & Messaging","m":False,"q":"An order needs to fan out to multiple independent downstream systems simultaneously — billing, shipping, and analytics — each of which should receive its own copy of the event. What pattern fits best?",
 "o":[
  {"t":"Publish the event to an SNS topic with billing, shipping, and analytics each subscribed via their own SQS queue.","c":True,"w":"SNS fan-out delivers a copy of every message to each subscriber, and subscribing SQS queues adds durability and independent consumption rates per downstream system."},
  {"t":"Send the event directly to a single SQS queue that all three systems poll.","c":False,"w":"A single SQS queue delivers each message to only one consumer, not to all three simultaneously — it would require the systems to compete for messages."},
  {"t":"Have the order service call each downstream system's API synchronously in sequence.","c":False,"w":"This tightly couples the services and means any one failure or slowdown blocks the whole chain, the opposite of a resilient fan-out design."},
  {"t":"Use a single Lambda function with shared state to track all three systems.","c":False,"w":"This reintroduces tight coupling and a single point of failure rather than using a decoupled fan-out pattern."}
 ]},
{"d":"Serverless & Messaging","m":False,"q":"A Lambda function occasionally times out when a downstream API is slow, and failed invocations need to be retried automatically without losing the event. What should you configure?",
 "o":[
  {"t":"A dead-letter queue (DLQ) or Lambda destination for failed asynchronous invocations.","c":True,"w":"For asynchronous invocations, Lambda retries automatically and a configured DLQ/destination captures events that still fail after retries, so nothing is silently lost."},
  {"t":"Increase the Lambda function's reserved concurrency to an arbitrarily high number.","c":False,"w":"Concurrency controls how many invocations run in parallel; it does not address retry behavior or lost events on failure."},
  {"t":"Disable function logging to reduce latency.","c":False,"w":"Disabling logging removes diagnostic visibility and has no effect on retry or failure handling."},
  {"t":"Switch the function's runtime to a compiled language.","c":False,"w":"Runtime choice may affect cold start time but doesn't address retries or failure capture for a slow downstream dependency."}
 ]},
{"d":"Serverless & Messaging","m":False,"q":"A workflow involves multiple Lambda functions that must run in a specific order, including conditional branches, retries, and a manual approval step. What service is purpose-built for this?",
 "o":[
  {"t":"AWS Step Functions.","c":True,"w":"Step Functions orchestrates exactly this kind of multi-step state machine, with native support for sequencing, branching, retries, and wait states such as manual approval."},
  {"t":"Amazon SQS standard queues.","c":False,"w":"SQS delivers messages but has no native concept of sequencing steps, branching logic, or orchestration across multiple functions."},
  {"t":"AWS CloudFormation.","c":False,"w":"CloudFormation provisions infrastructure as code; it does not orchestrate application-level runtime workflows."},
  {"t":"Amazon CloudWatch Events rules alone.","c":False,"w":"Basic EventBridge/CloudWatch rules route events to targets but don't manage multi-step state, branching, or approval waits as a unit."}
 ]},
{"d":"High Availability & DR","m":False,"q":"A company's DR requirement allows for several hours of downtime (RTO) and some data loss (RPO) in a disaster, and they want to minimize ongoing DR cost. Which DR strategy fits best?",
 "o":[
  {"t":"Backup and restore.","c":True,"w":"Backup and restore is the lowest-cost DR strategy, trading a longer recovery time (restoring from backups) for minimal ongoing infrastructure spend — appropriate when hours of downtime are acceptable."},
  {"t":"Multi-site active-active.","c":False,"w":"Active-active gives near-zero RTO/RPO but runs full production capacity in two locations continuously, the most expensive option — more than this requirement needs."},
  {"t":"Pilot light.","c":False,"w":"Pilot light is a reasonable middle ground but still costs more than backup and restore for a requirement that explicitly tolerates hours of downtime."},
  {"t":"Warm standby.","c":False,"w":"Warm standby runs a scaled-down but always-on version of the environment, costing more than necessary when several hours of downtime is acceptable."}
 ]},
{"d":"High Availability & DR","m":False,"q":"An Auto Scaling group spans three Availability Zones with a desired capacity of 6. One AZ becomes completely unavailable. What does the ASG do by default?",
 "o":[
  {"t":"It attempts to launch replacement instances in the remaining healthy Availability Zones to maintain the desired capacity.","c":True,"w":"ASG continuously works to keep the group at its desired capacity, so if one AZ's instances become unhealthy or unreachable, it launches new instances in the other AZs it's configured to use."},
  {"t":"It reduces the desired capacity to match only the healthy AZs.","c":False,"w":"The ASG does not reduce desired capacity on its own due to an AZ outage; it tries to maintain the configured desired count."},
  {"t":"It stops all instances in every AZ until the outage resolves.","c":False,"w":"ASG does not shut down healthy instances in response to one AZ's outage."},
  {"t":"It requires manual intervention to launch instances elsewhere.","c":False,"w":"This is precisely the kind of failure ASG is designed to handle automatically, without manual steps."}
 ]},
{"d":"High Availability & DR","m":False,"q":"How does Route 53 use health checks to support a failover routing policy between a primary and secondary endpoint?",
 "o":[
  {"t":"Route 53 continuously monitors the primary endpoint's health check and automatically routes traffic to the secondary endpoint only when the primary is marked unhealthy.","c":True,"w":"This is exactly how failover routing works: DNS answers stay pointed at the primary while it's healthy, and switch to the secondary automatically on failure, without any manual DNS change."},
  {"t":"Route 53 splits traffic evenly between primary and secondary at all times.","c":False,"w":"That describes weighted routing with equal weights, not failover routing, which favors the primary until it fails."},
  {"t":"Health checks only generate email alerts; routing changes still require a manual update.","c":False,"w":"Failover routing changes DNS answers automatically based on health check status — no manual update is required."},
  {"t":"Route 53 health checks can only monitor resources inside the same VPC.","c":False,"w":"Route 53 health checks can monitor endpoints over the public internet, not just resources within a single VPC."}
 ]},
{"d":"Cost Optimization","m":False,"q":"A company has steady-state compute usage across EC2, Fargate, and Lambda, and wants a flexible discount that applies automatically regardless of instance family or Region, without reserving specific instances.",
 "o":[
  {"t":"Savings Plans.","c":True,"w":"Savings Plans offer a discount in exchange for a commitment to a consistent amount of compute spend ($/hour), applying automatically across EC2, Fargate, and Lambda regardless of instance family or Region — unlike RIs, which are tied to specific instance attributes."},
  {"t":"Standard Reserved Instances in a single Region.","c":False,"w":"Standard RIs are tied to a specific instance family and Region (with limited flexibility), and don't cover Fargate or Lambda the way Savings Plans do."},
  {"t":"Spot Instances.","c":False,"w":"Spot is for interruption-tolerant workloads at variable discount, not a stable commitment-based discount for steady-state usage across multiple compute services."},
  {"t":"On-Demand pricing with no commitment.","c":False,"w":"On-Demand is the baseline price with no discount, which doesn't satisfy the goal of a flexible discount for committed usage."}
 ]},
{"d":"Cost Optimization","m":False,"q":"Which AWS tool proactively scans your account and recommends cost, performance, security, and fault-tolerance improvements, such as idle load balancers or underutilized EC2 instances?",
 "o":[
  {"t":"AWS Trusted Advisor.","c":True,"w":"Trusted Advisor inspects your account against best-practice checks across cost optimization, performance, security, and fault tolerance, flagging exactly this kind of idle or underutilized resource."},
  {"t":"AWS Budgets.","c":False,"w":"Budgets tracks spend against thresholds you set and sends alerts; it doesn't generate broad best-practice recommendations."},
  {"t":"AWS Cost Explorer.","c":False,"w":"Cost Explorer visualizes and analyzes historical and forecasted spend; it doesn't produce resource-level optimization recommendations the way Trusted Advisor does."},
  {"t":"AWS Config.","c":False,"w":"Config tracks resource configuration compliance over time; it is not primarily a cost/performance recommendation engine."}
 ]},
{"d":"Cost Optimization","m":False,"q":"An archive of compliance records must be retained for 7 years, accessed at most once a year, and retrieval can take up to 12 hours without issue. Which storage class minimizes cost?",
 "o":[
  {"t":"S3 Glacier Deep Archive.","c":True,"w":"Deep Archive is AWS's lowest-cost storage tier, built for data accessed rarely (roughly once a year or less) with retrieval times of hours, matching this exact access pattern."},
  {"t":"S3 Standard-IA.","c":False,"w":"Standard-IA offers millisecond retrieval at a higher storage cost than Deep Archive — unnecessary speed for data that's fine with a 12-hour retrieval window."},
  {"t":"S3 Glacier Instant Retrieval.","c":False,"w":"Instant Retrieval provides millisecond access at a higher cost than Deep Archive, which isn't needed when hours-long retrieval is acceptable."},
  {"t":"S3 Intelligent-Tiering.","c":False,"w":"Intelligent-Tiering is for unpredictable access patterns; it costs more than committing directly to Deep Archive when the access pattern (once a year) is already well known."}
 ]},
{"d":"Monitoring & Management","m":False,"q":"Which service should you use to record and audit every API call made within your AWS account, including who made it and when, for security analysis and compliance?",
 "o":[
  {"t":"AWS CloudTrail.","c":True,"w":"CloudTrail logs API activity across your account — the caller identity, time, source IP, and request/response details — which is exactly what security auditing and compliance investigations need."},
  {"t":"Amazon CloudWatch.","c":False,"w":"CloudWatch focuses on operational metrics, logs you send to it, and alarms; it is not the service that automatically records account-wide API call history."},
  {"t":"AWS Config.","c":False,"w":"Config tracks the configuration state and change history of resources, not the individual API calls that caused those changes."},
  {"t":"AWS X-Ray.","c":False,"w":"X-Ray traces requests through distributed application code for performance debugging, not account-level API auditing."}
 ]},
{"d":"Monitoring & Management","m":False,"q":"You want to be notified automatically, and trigger an automated remediation action, the moment an EC2 instance's CPU utilization exceeds 90% for 5 consecutive minutes. What should you configure?",
 "o":[
  {"t":"A CloudWatch Alarm on the CPUUtilization metric that triggers an SNS notification and an Auto Scaling or Lambda-based remediation action.","c":True,"w":"CloudWatch Alarms watch a metric against a threshold over a defined period and can directly trigger actions like SNS notifications, Auto Scaling policies, or Lambda functions — exactly this requirement."},
  {"t":"An AWS Config rule evaluated once per day.","c":False,"w":"Config rules evaluate configuration compliance, not real-time performance metrics, and a daily evaluation is far too slow for a 5-minute threshold."},
  {"t":"A CloudTrail trail with S3 log delivery.","c":False,"w":"CloudTrail records API calls, not instance performance metrics, and has no built-in alarming/remediation trigger."},
  {"t":"Manually checking the EC2 console dashboard periodically.","c":False,"w":"This isn't automated and would miss the requirement for immediate, automatic notification and remediation."}
 ]},
{"d":"Monitoring & Management","m":False,"q":"A company wants to continuously track whether their S3 buckets ever become publicly accessible and automatically flag non-compliant resources against an internal policy. What should they use?",
 "o":[
  {"t":"AWS Config with a managed rule for S3 bucket public access, combined with automatic compliance evaluation.","c":True,"w":"Config continuously evaluates resource configurations against rules — including prebuilt managed rules for public S3 access — and records compliance status over time, which directly matches this requirement."},
  {"t":"Amazon CloudWatch Logs Insights queries run manually once a week.","c":False,"w":"Manual weekly queries aren't continuous monitoring and wouldn't catch a bucket becoming public in between checks."},
  {"t":"AWS Billing Alerts.","c":False,"w":"Billing alerts track spend thresholds, which is unrelated to bucket access configuration."},
  {"t":"VPC Flow Logs.","c":False,"w":"Flow Logs capture network traffic metadata at the VPC level; they don't evaluate S3 bucket policy configuration."}
 ]}
]

rng = random.Random(42)
for item in Q:
    rng.shuffle(item["o"])

out_path = Path(__file__).resolve().parent.parent / "data" / "curated.json"
out_path.write_text(json.dumps(Q, ensure_ascii=False), encoding="utf-8")
print("Wrote", out_path, "with", len(Q), "questions")
