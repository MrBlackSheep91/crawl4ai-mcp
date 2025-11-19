"""
Second Brain Integration Tests
Tests the complete flow: Crawl4AI → ChromaDB → Graphiti

Requirements:
pip install httpx pytest
"""
import sys
import io

# Fix Windows encoding for emojis
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import httpx
import asyncio
import json
from datetime import datetime
from typing import Dict, Any

# Service URLs
CRAWL4AI_URL = "https://crawl4ai-production-7ab7.up.railway.app"
GRAPHITI_URL = "https://graphiti-oozt-production.up.railway.app"

# Test configuration
TEST_URL = "https://docs.railway.app/guides/deployments"
TEST_QUERY = "How to deploy applications"
GROUP_ID = "maicol_second_brain"


class IntegrationTester:
    """Integration testing suite for Second Brain"""

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests_passed": 0,
            "tests_failed": 0,
            "details": []
        }

    async def test_health_endpoints(self) -> bool:
        """Test 1: Verify all services are healthy"""
        print("\n🧪 Test 1: Health Endpoints")
        print("-" * 50)

        try:
            # Test Crawl4AI
            resp = await self.client.get(f"{CRAWL4AI_URL}/health")
            assert resp.status_code == 200, f"Crawl4AI health check failed: {resp.status_code}"

            data = resp.json()
            assert data["status"] == "healthy", f"Crawl4AI not healthy: {data}"
            assert "chroma_url" in data, "ChromaDB URL missing"

            print(f"✅ Crawl4AI: {data['status']}")
            print(f"   ChromaDB: {data['chroma_url']}")
            print(f"   Collection: {data['collection']} ({data['collection_count']} docs)")

            # Test Graphiti
            resp = await self.client.get(f"{GRAPHITI_URL}/healthcheck")
            assert resp.status_code == 200, f"Graphiti health check failed: {resp.status_code}"

            data = resp.json()
            assert data["status"] == "healthy", f"Graphiti not healthy: {data}"

            print(f"✅ Graphiti: {data['status']}")

            self.results["tests_passed"] += 1
            self.results["details"].append({
                "test": "health_endpoints",
                "status": "PASSED",
                "message": "All services healthy"
            })
            return True

        except Exception as e:
            print(f"❌ Health check failed: {e}")
            self.results["tests_failed"] += 1
            self.results["details"].append({
                "test": "health_endpoints",
                "status": "FAILED",
                "error": str(e)
            })
            return False

    async def test_crawl_and_index(self) -> bool:
        """Test 2: Crawl URL and index in ChromaDB"""
        print("\n🧪 Test 2: Crawl and Index")
        print("-" * 50)

        try:
            # Crawl the documentation
            payload = {
                "url": TEST_URL,
                "max_depth": 1,
                "chunk_size": 1000
            }

            print(f"📥 Crawling: {TEST_URL}")
            resp = await self.client.post(
                f"{CRAWL4AI_URL}/crawl",
                json=payload
            )

            assert resp.status_code == 200, f"Crawl failed: {resp.status_code} - {resp.text}"

            data = resp.json()
            assert data["success"] == True, f"Crawl not successful: {data}"
            assert data["chunks_added"] > 0, "No chunks were added"

            print(f"✅ Crawled successfully")
            print(f"   URL: {data['url']}")
            print(f"   Chunks added: {data['chunks_added']}")
            print(f"   Message: {data['message']}")

            self.results["tests_passed"] += 1
            self.results["details"].append({
                "test": "crawl_and_index",
                "status": "PASSED",
                "chunks_added": data["chunks_added"],
                "url": data["url"]
            })
            return True

        except Exception as e:
            print(f"❌ Crawl failed: {e}")
            self.results["tests_failed"] += 1
            self.results["details"].append({
                "test": "crawl_and_index",
                "status": "FAILED",
                "error": str(e)
            })
            return False

    async def test_semantic_search(self) -> Dict[str, Any]:
        """Test 3: Semantic search in ChromaDB"""
        print("\n🧪 Test 3: Semantic Search")
        print("-" * 50)

        try:
            payload = {
                "query": TEST_QUERY,
                "n_results": 3
            }

            print(f"🔍 Searching: '{TEST_QUERY}'")
            resp = await self.client.post(
                f"{CRAWL4AI_URL}/search",
                json=payload
            )

            assert resp.status_code == 200, f"Search failed: {resp.status_code} - {resp.text}"

            data = resp.json()
            assert "results" in data, "No results field in response"
            assert len(data["results"]) > 0, "No search results found"

            print(f"✅ Search successful")
            print(f"   Results found: {len(data['results'])}")

            # Display top result
            top_result = data["results"][0]
            print(f"\n   📄 Top Result:")
            print(f"      Distance: {top_result['distance']:.4f}")
            print(f"      Source: {top_result['metadata'].get('source_url', 'N/A')}")
            print(f"      Preview: {top_result['content'][:150]}...")

            self.results["tests_passed"] += 1
            self.results["details"].append({
                "test": "semantic_search",
                "status": "PASSED",
                "results_count": len(data["results"]),
                "top_distance": top_result['distance']
            })

            return data["results"]

        except Exception as e:
            print(f"❌ Search failed: {e}")
            self.results["tests_failed"] += 1
            self.results["details"].append({
                "test": "semantic_search",
                "status": "FAILED",
                "error": str(e)
            })
            return []

    async def test_graphiti_integration(self, search_results: list) -> bool:
        """Test 4: Send data to Graphiti knowledge graph"""
        print("\n🧪 Test 4: Graphiti Integration")
        print("-" * 50)

        if not search_results:
            print("⚠️  Skipping - no search results to send")
            return False

        try:
            # Format messages for Graphiti
            messages = []
            for idx, result in enumerate(search_results[:3]):  # Top 3 results
                messages.append({
                    "content": result["content"],
                    "role": "system",
                    "role_type": "system",
                    "timestamp": datetime.now().isoformat(),
                    "metadata": {
                        "source": "crawl4ai",
                        "source_url": result["metadata"].get("source_url", ""),
                        "relevance_score": result["distance"],
                        "chunk_index": result["metadata"].get("chunk_index", idx)
                    }
                })

            payload = {
                "group_id": GROUP_ID,
                "messages": messages
            }

            print(f"📤 Sending {len(messages)} messages to Graphiti")
            resp = await self.client.post(
                f"{GRAPHITI_URL}/messages",
                json=payload
            )

            assert resp.status_code in [200, 202], f"Graphiti failed: {resp.status_code} - {resp.text}"

            data = resp.json()
            print(f"✅ Graphiti integration successful")
            print(f"   Messages sent: {len(messages)}")
            print(f"   Group ID: {GROUP_ID}")

            # Optional: Verify entities were created
            try:
                search_resp = await self.client.post(
                    f"{GRAPHITI_URL}/search",
                    json={"query": TEST_QUERY, "group_id": GROUP_ID, "num_results": 5}
                )

                if search_resp.status_code == 200:
                    search_data = search_resp.json()
                    print(f"   Entities created: {len(search_data.get('nodes', []))} nodes, {len(search_data.get('edges', []))} edges")
            except:
                pass  # Search verification is optional

            self.results["tests_passed"] += 1
            self.results["details"].append({
                "test": "graphiti_integration",
                "status": "PASSED",
                "messages_sent": len(messages),
                "group_id": GROUP_ID
            })
            return True

        except Exception as e:
            print(f"❌ Graphiti integration failed: {e}")
            self.results["tests_failed"] += 1
            self.results["details"].append({
                "test": "graphiti_integration",
                "status": "FAILED",
                "error": str(e)
            })
            return False

    async def test_stats(self) -> bool:
        """Test 5: Verify stats endpoints"""
        print("\n🧪 Test 5: Stats Verification")
        print("-" * 50)

        try:
            # Get Crawl4AI stats
            resp = await self.client.get(f"{CRAWL4AI_URL}/stats")
            assert resp.status_code == 200, f"Stats failed: {resp.status_code}"

            data = resp.json()
            print(f"✅ Stats retrieved")
            print(f"   Collection: {data['collection_name']}")
            print(f"   Total documents: {data['total_documents']}")
            print(f"   ChromaDB URL: {data['chroma_url']}")

            assert data['total_documents'] > 0, "No documents in collection"

            self.results["tests_passed"] += 1
            self.results["details"].append({
                "test": "stats_verification",
                "status": "PASSED",
                "total_documents": data['total_documents']
            })
            return True

        except Exception as e:
            print(f"❌ Stats verification failed: {e}")
            self.results["tests_failed"] += 1
            self.results["details"].append({
                "test": "stats_verification",
                "status": "FAILED",
                "error": str(e)
            })
            return False

    async def run_all_tests(self):
        """Run complete integration test suite"""
        print("=" * 50)
        print("🚀 Second Brain Integration Tests")
        print("=" * 50)
        print(f"Started: {self.results['timestamp']}")
        print(f"Crawl4AI: {CRAWL4AI_URL}")
        print(f"Graphiti: {GRAPHITI_URL}")

        try:
            # Run tests in sequence
            if not await self.test_health_endpoints():
                print("\n❌ Health checks failed - aborting tests")
            elif not await self.test_crawl_and_index():
                print("\n❌ Crawl failed - aborting remaining tests")
            else:
                search_results = await self.test_semantic_search()
                await self.test_graphiti_integration(search_results)
                await self.test_stats()

            # Final summary
            print("\n" + "=" * 50)
            print("📊 Test Summary")
            print("=" * 50)
            print(f"✅ Passed: {self.results['tests_passed']}")
            print(f"❌ Failed: {self.results['tests_failed']}")
            total_tests = self.results['tests_passed'] + self.results['tests_failed']
            if total_tests > 0:
                print(f"📈 Success Rate: {(self.results['tests_passed'] / total_tests * 100):.1f}%")

            # Save results
            with open("test_results.json", "w") as f:
                json.dump(self.results, f, indent=2)

            print(f"\n💾 Results saved to: test_results.json")

            return self.results

        finally:
            await self.client.aclose()


async def main():
    """Main test runner"""
    tester = IntegrationTester()
    results = await tester.run_all_tests()

    # Exit with error code if tests failed
    if results["tests_failed"] > 0:
        exit(1)
    else:
        exit(0)


if __name__ == "__main__":
    asyncio.run(main())
