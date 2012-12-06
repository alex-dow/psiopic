package com.psikon;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

import com.psikon.parsers.W;

import de.l3s.boilerpipe.BoilerpipeProcessingException;
import de.l3s.boilerpipe.extractors.ArticleExtractor;
import de.l3s.boilerpipe.extractors.ArticleSentencesExtractor;
//import de.l3s.boilerpipe.extractors.ArticleExtractor;

import info.bliki.wiki.filter.HTMLConverter;

/**
 * Boilerclog - A mediawiki body of content extractor
 * 
 * Runs by reading a mediawiki page, then returning the main body of content
 * of that page on standard output.
 * 
 * Example usage:
 * 
 * cat mediawikipage.html | java -jar boilerclog.jar
 */
public class Boilerclog {

	/**
	 * Main method
	 * 
	 * @param args    This script takes no arguments
	 * @throws IOException 
	 * @throws BoilerpipeProcessingException 
	 */
	public static void main(String[] args) throws IOException, BoilerpipeProcessingException {

		String inputString; 
		
		BufferedReader in = new BufferedReader(new InputStreamReader(System.in));
		StringBuilder input = new StringBuilder();
		char[] buffer = new char[4096];
		int read = 0;
		
		do {
			input.append(buffer,0,read);
			read = in.read(buffer);
		} while (read >= 0);
		
		inputString = input.toString();		
		
		inputString = Boilerclog.toHtml(inputString);
		System.out.println(ArticleSentencesExtractor.INSTANCE.getText(inputString));
	}
	
	/**
	 * Converts mediawiki syntax into html
	 * 
	 * @param inputString   The input string containing the mediawiki syntax
	 * @return String       Wild guess what this is...
	 * @throws IOException
	 */
	protected static String toHtml(String inputString) throws IOException
	{
		StringBuilder resultBuffer = new StringBuilder(inputString.length() + inputString.length() / 10);

		// TODO Are the contructor arguments necessary??
		WikiNewsModel model = new WikiNewsModel("/${image}", "/${title}");
		model.addTemplateFunction("w", W.CONST);
		HTMLConverter modelConverter = new HTMLConverter();
		model.render(modelConverter, inputString, resultBuffer, false, true);
		return resultBuffer.toString();
	}
}
